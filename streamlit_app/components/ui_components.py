"""
Reusable UI components for IBVAP Streamlit app.
"""
import streamlit as st
import pandas as pd
from typing import Optional
from utils.data_service import IntrusionEvent


def risk_badge(risk: str) -> str:
    colors = {
        "HIGH": ("#fee2e2", "#dc2626", "#fecaca"),
        "MEDIUM": ("#fef3c7", "#d97706", "#fde68a"),
        "LOW": ("#ccfbf1", "#0d9488", "#99f6e4"),
    }
    bg, text, border = colors.get(risk, colors["LOW"])
    return f"""<span style="background:{bg};color:{text};border:1px solid {border};
    padding:2px 10px;border-radius:6px;font-size:11px;font-weight:600;">
    &#9679; {risk}</span>"""


def status_indicator(online: bool, label: str = "") -> str:
    color = "#22c55e" if online else "#ef4444"
    dot = f'<span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:{color};margin-right:6px;"></span>'
    if label:
        return f'{dot}<span style="font-size:12px;font-weight:500;color:{"#16a34a" if online else "#dc2626"};">{label}</span>'
    return dot


def metric_card_html(label: str, value: str, icon: str, accent: str = "teal") -> str:
    accent_colors = {
        "teal": ("#f0fdfa", "#0d9488"),
        "red": ("#fef2f2", "#dc2626"),
        "amber": ("#fffbeb", "#d97706"),
        "green": ("#f0fdf4", "#16a34a"),
        "navy": ("var(--secondary-background-color)", "var(--text-color)"),
    }
    bg, text = accent_colors.get(accent, accent_colors["teal"])
    return f"""
    <div style="background:var(--background-color);border:1px solid var(--secondary-background-color);border-radius:12px;padding:20px;
    transition:all 0.2s;" onmouseover="this.style.boxShadow='0 4px 12px rgba(0,0,0,0.08)'"
    onmouseout="this.style.boxShadow='none'">
        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px;">
            <div style="width:44px;height:44px;border-radius:10px;background:{bg};display:flex;
            align-items:center;justify-content:center;font-size:20px;color:{text};">{icon}</div>
        </div>
        <p style="font-size:28px;font-weight:700;color:var(--text-color);margin:0;line-height:1.2;">{value}</p>
        <p style="font-size:13px;color:var(--text-color);opacity:0.7;margin:4px 0 0 0;">{label}</p>
    </div>"""





def pipeline_step_html(icon: str, label: str, desc: str, is_last: bool = False) -> str:
    arrow = "" if is_last else '<div style="text-align:center;color:var(--text-color);opacity:0.5;font-size:18px;padding:4px 0;">&darr;</div>'
    return f"""
    <div style="display:flex;align-items:center;gap:12px;padding:10px 14px;background:var(--secondary-background-color);
    border:1px solid var(--secondary-background-color);border-radius:10px;margin-bottom:4px;">
        <div style="width:36px;height:36px;border-radius:8px;background:var(--background-color);border:1px solid var(--secondary-background-color);
        display:flex;align-items:center;justify-content:center;font-size:16px;flex-shrink:0;">{icon}</div>
        <div>
            <div style="font-size:13px;font-weight:600;color:var(--text-color);">{label}</div>
            <div style="font-size:11px;color:var(--text-color);opacity:0.7;">{desc}</div>
        </div>
    </div>{arrow}"""


def security_pipeline_html() -> str:
    steps = [
        ("&#127909;", "Video Input", "Surveillance feed"),
        ("&#129504;", "YOLO11 Detection", "Person detection"),
        ("&#127919;", "ByteTrack Tracking", "Multi-object tracking"),
        ("&#128205;", "Zone Analysis", "Restricted zone check"),
        ("&#128680;", "Intrusion Detection", "Zone entry event"),
        ("&#9201;", "Timestamp", "Frame & time"),
        ("&#9888;", "Risk Classification", "HIGH / MEDIUM / LOW"),
        ("&#128247;", "Evidence Capture", "Visual snapshot"),
        ("&#129534;", "Audit Log", "Structured record"),
    ]
    parts = [f'<div style="font-size:14px;font-weight:600;color:var(--text-color);margin-bottom:10px;">AI Security Pipeline</div>']
    for i, (icon, label, desc) in enumerate(steps):
        parts.append(pipeline_step_html(icon, label, desc, is_last=(i == len(steps) - 1)))
    return "".join(parts)


def empty_state_html(icon: str, title: str, description: str) -> str:
    return f"""
    <div style="text-align:center;padding:48px 20px;">
        <div style="width:64px;height:64px;border-radius:16px;background:var(--secondary-background-color);display:flex;
        align-items:center;justify-content:center;margin:0 auto 16px;font-size:28px;">{icon}</div>
        <h3 style="font-size:16px;font-weight:600;color:var(--text-color);margin:0 0 4px 0;">{title}</h3>
        <p style="font-size:13px;color:var(--text-color);opacity:0.7;max-width:400px;margin:0 auto;">{description}</p>
    </div>"""


def section_header(title: str, subtitle: str = "") -> str:
    sub = f'<p style="font-size:13px;color:var(--text-color);opacity:0.7;margin:2px 0 0 0;">{subtitle}</p>' if subtitle else ""
    return f"""
    <div style="margin-bottom:16px;">
        <h2 style="font-size:20px;font-weight:700;color:var(--text-color);margin:0;">{title}</h2>
        {sub}
    </div>"""


def info_card(title: str, content_html: str) -> str:
    return f"""
    <div style="background:var(--background-color);border:1px solid var(--secondary-background-color);border-radius:12px;padding:20px;">
        <div style="font-size:14px;font-weight:600;color:var(--text-color);margin-bottom:12px;">{title}</div>
        {content_html}
    </div>"""
