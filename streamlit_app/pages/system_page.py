"""System page — technical system information & architecture."""
import streamlit as st

from components.ui_components import (
    security_pipeline_html, section_header, status_indicator
)


def render(events):
    st.markdown(section_header("System", "Technical system information & architecture"), unsafe_allow_html=True)

    # Project info
    st.markdown("""
    <div class="ibvap-card">
        <div style="display:flex;align-items:center;gap:12px;">
            <div style="width:40px;height:40px;border-radius:10px;
            background:linear-gradient(135deg,#14b8a6,#0d9488);
            display:flex;align-items:center;justify-content:center;font-size:18px;">🛡️</div>
            <div>
                <h3 style="margin:0;font-size:16px;font-weight:700;color:#0f172a;">IBVAP</h3>
                <p style="margin:0;font-size:12px;color:#94a3b8;">Intelligent Border Video Analytics Platform</p>
            </div>
            <div style="margin-left:auto;display:flex;align-items:center;gap:6px;
            padding:6px 12px;border-radius:8px;background:#dcfce7;border:1px solid #bbf7d0;">
                <span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:#22c55e;"></span>
                <span style="font-size:12px;font-weight:600;color:#16a34a;">OPERATIONAL</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Module grid
    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
    modules = [
        ("🧠", "AI Detection", "YOLO11", "Person detection model"),
        ("🎯", "Object Tracking", "ByteTrack", "Multi-object tracking"),
        ("👁️", "Video Processing", "OpenCV", "Frame processing & annotation"),
        ("📍", "Restricted Zone", "Polygon-based", "Zone detection & analysis"),
        ("⚠️", "Risk Engine", "HIGH for intrusion", "Zone entry risk classification"),
        ("🧾", "Security Logging", "CSV audit log", "Structured event records"),
        ("🖥️", "Frontend", "Streamlit + Python", "Modern web application"),
    ]

    cols = st.columns(3)
    for i, (icon, label, value, desc) in enumerate(modules):
        with cols[i % 3]:
            st.markdown(f"""
            <div class="ibvap-card" style="padding:16px;">
                <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px;">
                    <div style="width:36px;height:36px;border-radius:8px;background:#f0fdfa;
                    display:flex;align-items:center;justify-content:center;font-size:16px;">{icon}</div>
                    <span style="font-size:13px;font-weight:500;color:#475569;">{label}</span>
                </div>
                <p style="font-size:15px;font-weight:700;color:#0f172a;margin:0;">{value}</p>
                <p style="font-size:11px;color:#94a3b8;margin:4px 0 0 0;">{desc}</p>
            </div>
            """, unsafe_allow_html=True)

    # Security pipeline
    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
    st.markdown(f'<div class="pipeline-container">{security_pipeline_html()}</div>', unsafe_allow_html=True)

    # Cybersecurity architecture
    st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)
    st.markdown("#### Cybersecurity Architecture")

    col_current, col_future = st.columns(2)

    with col_current:
        steps = ["Video", "AI Detection", "Tracking", "Intrusion Event", "Audit Record"]
        steps_html = ""
        for i, step in enumerate(steps):
            steps_html += f"""
            <div style="display:flex;align-items:center;gap:8px;padding:6px 0;font-size:13px;color:#475569;">
                <span style="color:#22c55e;">✓</span> {step}
            </div>"""
        st.markdown(f"""
        <div class="ibvap-card">
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:12px;">
                <span style="font-size:16px;">📊</span>
                <h3 style="margin:0;">Current Architecture</h3>
            </div>
            {steps_html}
        </div>
        """, unsafe_allow_html=True)

    with col_future:
        steps = ["Audit Record", "Cryptographic Hash", "Permissioned Blockchain", "Tamper-Evident Record"]
        steps_html = ""
        for i, step in enumerate(steps):
            steps_html += f"""
            <div style="display:flex;align-items:center;gap:8px;padding:6px 0;font-size:13px;color:#94a3b8;">
                <span style="display:inline-block;width:14px;height:14px;border-radius:50%;
                border:1px solid #cbd5e1;"></span> {step}
            </div>"""
        st.markdown(f"""
        <div class="ibvap-card" style="border:2px dashed #cbd5e1;">
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:12px;">
                <span style="font-size:16px;">📊</span>
                <div>
                    <h3 style="margin:0;">Future Architecture</h3>
                    <span style="font-size:10px;font-weight:600;color:#d97706;">FUTURE ENHANCEMENT</span>
                </div>
            </div>
            {steps_html}
            <p style="font-size:12px;color:#94a3b8;margin-top:12px;padding-top:12px;
            border-top:1px solid #f1f5f9;">
            Blockchain storage is future scope. Not yet implemented.</p>
        </div>
        """, unsafe_allow_html=True)
