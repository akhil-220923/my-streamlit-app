"""Surveillance page — border surveillance monitoring & analysis."""
import streamlit as st

from components.ui_components import (
    risk_badge, status_indicator, section_header, empty_state_html
)
from utils.data_service import get_video_path, timestamp_to_seconds


def render(events):
    st.markdown(section_header("Surveillance", "Border surveillance monitoring & analysis"), unsafe_allow_html=True)

    video_path = get_video_path()

    col_video, col_zone = st.columns([2, 1])

    with col_video:
        # Camera header
        st.markdown("""
        <div class="ibvap-card" style="padding:0;overflow:hidden;">
            <div style="display:flex;align-items:center;justify-content:space-between;
            padding:12px 16px;border-bottom:1px solid #e2e8f0;background:#f8fafc;">
                <div style="display:flex;align-items:center;gap:8px;">
                    <span style="font-size:14px;">📹</span>
                    <span style="font-size:14px;font-weight:600;color:#1e293b;">Border Surveillance Feed</span>
                    <span style="font-size:12px;color:#94a3b8;font-family:monospace;">CAM-01</span>
                </div>
                <div style="display:flex;align-items:center;gap:6px;">
                    <span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:#22c55e;
                    animation:pulse 2s infinite;"></span>
                    <span style="font-size:12px;font-weight:600;color:#0d9488;">PROCESSED</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if video_path:
            st.video(video_path)
        else:
            # Simulated surveillance feed
            st.markdown("""
            <div style="background:#0a1929;aspect-ratio:16/9;border-radius:0 0 12px 12px;
            position:relative;overflow:hidden;">
                <!-- Grid overlay -->
                <div style="position:absolute;inset:0;opacity:0.15;
                background-image:linear-gradient(rgba(45,212,191,0.3) 1px,transparent 1px),
                linear-gradient(90deg,rgba(45,212,191,0.3) 1px,transparent 1px);
                background-size:40px 40px;"></div>
                <!-- Restricted zone -->
                <svg style="position:absolute;inset:0;width:100%;height:100%;" preserveAspectRatio="none" viewBox="0 0 100 56">
                    <polygon points="30,20 70,20 75,45 25,45" fill="rgba(239,68,68,0.08)"
                    stroke="rgba(239,68,68,0.5)" stroke-width="0.3" stroke-dasharray="1,1"/>
                    <text x="50" y="36" fill="rgba(239,68,68,0.6)" font-size="2" text-anchor="middle"
                    font-family="monospace">RESTRICTED ZONE</text>
                </svg>
                <!-- Bounding boxes -->
                <div style="position:absolute;top:30%;left:35%;width:64px;height:96px;
                border:2px solid rgba(45,212,191,0.6);border-radius:2px;">
                    <span style="position:absolute;top:-20px;left:0;font-size:10px;
                    font-family:monospace;color:#5eead4;background:rgba(10,25,41,0.8);
                    padding:1px 4px;border-radius:2px;">ID:2</span>
                </div>
                <div style="position:absolute;top:45%;left:55%;width:56px;height:80px;
                border:2px solid rgba(239,68,68,0.7);border-radius:2px;">
                    <span style="position:absolute;top:-20px;left:0;font-size:10px;
                    font-family:monospace;color:#fca5a5;background:rgba(10,25,41,0.8);
                    padding:1px 4px;border-radius:2px;">ID:7 INTRUSION</span>
                </div>
                <div style="position:absolute;inset:0;display:flex;align-items:center;
                justify-content:center;flex-direction:column;">
                    <span style="font-size:48px;">📹</span>
                    <p style="color:#64748b;font-size:14px;margin:8px 0 0 0;">
                    Processed Surveillance Video Unavailable</p>
                    <p style="color:#475569;font-size:12px;margin:4px 0 0 0;">
                    Expected: output/final_intrusion_video.mp4</p>
                </div>
            </div>
            """, unsafe_allow_html=True)

    with col_zone:
        # Restricted zone panel
        st.markdown("""
        <div class="ibvap-card">
            <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px;">
                <div style="display:flex;align-items:center;gap:8px;">
                    <div style="width:32px;height:32px;border-radius:8px;background:#fef2f2;
                    display:flex;align-items:center;justify-content:center;">📍</div>
                    <h3 style="margin:0;">Restricted Zone</h3>
                </div>
                <div style="display:flex;align-items:center;gap:6px;">
                    <span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:#22c55e;"></span>
                    <span style="font-size:12px;font-weight:600;color:#0d9488;">MONITORED</span>
                </div>
            </div>
            <div class="zone-viz">
                <div style="position:absolute;inset:0;opacity:0.3;
                background-image:linear-gradient(rgba(45,212,191,0.15) 1px,transparent 1px),
                linear-gradient(90deg,rgba(45,212,191,0.15) 1px,transparent 1px);
                background-size:24px 24px;"></div>
                <svg style="position:absolute;inset:0;width:100%;height:100%;"
                preserveAspectRatio="none" viewBox="0 0 200 160">
                    <polygon points="60,40 140,40 150,120 50,120" fill="rgba(239,68,68,0.1)"
                    stroke="rgba(239,68,68,0.6)" stroke-width="1" stroke-dasharray="4,3"/>
                    <text x="100" y="85" fill="rgba(239,68,68,0.7)" font-size="7"
                    text-anchor="middle" font-family="monospace">RESTRICTED ZONE</text>
                    <circle cx="75" cy="70" r="3" fill="rgba(45,212,191,0.8)"/>
                    <text x="75" y="65" fill="rgba(45,212,191,0.9)" font-size="5"
                    text-anchor="middle" font-family="monospace">T:2</text>
                    <circle cx="110" cy="95" r="3" fill="rgba(239,68,68,0.8)"/>
                    <text x="110" y="90" fill="rgba(239,68,68,0.9)" font-size="5"
                    text-anchor="middle" font-family="monospace">T:7</text>
                    <circle cx="130" cy="110" r="3" fill="rgba(239,68,68,0.8)"/>
                    <text x="130" y="105" fill="rgba(239,68,68,0.9)" font-size="5"
                    text-anchor="middle" font-family="monospace">T:36</text>
                </svg>
            </div>
            <div style="display:flex;gap:16px;margin-bottom:10px;">
                <div style="display:flex;align-items:center;gap:6px;">
                    <span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:#22c55e;"></span>
                    <span style="font-size:12px;color:#475569;">Normal</span>
                </div>
                <div style="display:flex;align-items:center;gap:6px;">
                    <span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:#ef4444;"></span>
                    <span style="font-size:12px;color:#475569;">Intrusion</span>
                </div>
            </div>
            <p style="font-size:12px;color:#94a3b8;line-height:1.5;margin:0;">
            The system detects whether a tracked person enters the configured restricted area.
            Person Track IDs are ByteTrack session identifiers and do not represent permanent
            real-world identities.</p>
        </div>
        """, unsafe_allow_html=True)

    # Event timeline
    st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)

    col_timeline, col_detail = st.columns([2, 1])

    with col_timeline:
        st.markdown("""
        <div class="ibvap-card">
            <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:14px;">
                <h3 style="margin:0;">Event Timeline</h3>
                <span style="font-size:12px;color:#94a3b8;">{} events</span>
            </div>
        """.format(len(events)), unsafe_allow_html=True)

        if not events:
            st.markdown("""
            <p style="text-align:center;color:#94a3b8;padding:24px;">
            No intrusion events detected.</p>
            """, unsafe_allow_html=True)
        else:
            def _select_event(eid):
                st.session_state.ibvap_selected_event = eid

            for event in events:
                st.button(
                    f"🔴 {event.timestamp} — {event.event_type} — Track {event.person_track_id} — Frame {event.frame}",
                    key=f"timeline-{event.event_id}",
                    use_container_width=True,
                    type="primary" if st.session_state.get("ibvap_selected_event") == event.event_id else "secondary",
                    on_click=_select_event,
                    args=(event.event_id,)
                )

        st.markdown("</div>", unsafe_allow_html=True)

    with col_detail:
        selected_id = st.session_state.get("ibvap_selected_event")
        selected = next((e for e in events if e.event_id == selected_id), None)

        if selected:
            st.markdown(f"""
            <div class="ibvap-card">
                <h3>Selected Event</h3>
                <div style="display:flex;justify-content:space-between;padding:8px 0;">
                    <span style="font-size:13px;color:#94a3b8;">Event ID</span>
                    <span style="font-size:13px;font-family:monospace;font-weight:500;color:#1e293b;">{selected.event_id}</span>
                </div>
                <div style="display:flex;justify-content:space-between;padding:8px 0;">
                    <span style="font-size:13px;color:#94a3b8;">Track ID</span>
                    <span style="font-size:13px;font-weight:500;color:#1e293b;">Track {selected.person_track_id}</span>
                </div>
                <div style="display:flex;justify-content:space-between;padding:8px 0;">
                    <span style="font-size:13px;color:#94a3b8;">Timestamp</span>
                    <span style="font-size:13px;font-family:monospace;font-weight:500;color:#1e293b;">{selected.timestamp}</span>
                </div>
                <div style="display:flex;justify-content:space-between;padding:8px 0;">
                    <span style="font-size:13px;color:#94a3b8;">Frame</span>
                    <span style="font-size:13px;font-family:monospace;font-weight:500;color:#1e293b;">{selected.frame}</span>
                </div>
                <div style="display:flex;justify-content:space-between;padding:8px 0;">
                    <span style="font-size:13px;color:#94a3b8;">Risk</span>
                    {risk_badge(selected.risk)}
                </div>
            </div>
            """, unsafe_allow_html=True)

            if selected.evidence_file:
                def _view_evidence(eid):
                    st.session_state.ibvap_evidence_view = eid
                    st.session_state.ibvap_page = "digital-evidence"

                st.button(
                    "View Evidence",
                    key="surv-view-evidence",
                    use_container_width=True,
                    on_click=_view_evidence,
                    args=(selected.event_id,)
                )
        else:
            st.markdown("""
            <div class="ibvap-card">
                <p style="text-align:center;color:#94a3b8;padding:24px;">
                Select an event from the timeline to view details.</p>
            </div>
            """, unsafe_allow_html=True)
