"""
IBVAP — Intelligent Border Video Analytics Platform
Data service layer.

Reads intrusion events from Supabase (if configured) or falls back to
the local CSV file at output/intrusion_log.csv.
"""
import os
import csv
import io
import json
from dataclasses import dataclass, asdict, field
from typing import Optional
from datetime import datetime

import pandas as pd
import streamlit as st

SUPABASE_URL = os.environ.get("SUPABASE_URL") or os.environ.get("VITE_SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_ANON_KEY") or os.environ.get("VITE_SUPABASE_ANON_KEY", "")

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

CSV_PATH = os.path.join(PROJECT_ROOT, "output", "intrusion_log.csv")
EVIDENCE_DIR = os.path.join(PROJECT_ROOT, "output", "evidence")
VIDEO_PATH = os.path.join(PROJECT_ROOT, "output", "final_intrusion_video.mp4")


@dataclass
class IntrusionEvent:
    event_id: str
    event_type: str
    person_track_id: int
    frame: int
    timestamp: str
    risk: str
    evidence_file: Optional[str]
    status: str
    detection_method: str
    created_at: str = ""

    def to_dict(self):
        return asdict(self)


def _find_evidence_file(event_id: str, track_id: int, frame: int) -> Optional[str]:
    """Helper to locate local evidence image file in output/evidence directory."""
    if not os.path.exists(EVIDENCE_DIR):
        return None
    try:
        files = os.listdir(EVIDENCE_DIR)
        for fname in files:
            if fname.startswith(event_id) or f"track_{track_id}_frame_{frame}" in fname:
                return os.path.join(EVIDENCE_DIR, fname)
    except Exception:
        pass
    return None


def _seed_events() -> list[IntrusionEvent]:
    """Fallback seed data matching the prototype output."""
    raw_seeds = [
        ("EVT-001", "Zone Entry", 2, 30, "00:01.20", "HIGH", "https://images.pexels.com/photos/13530045/pexels-photo-13530045.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"),
        ("EVT-002", "Zone Entry", 7, 108, "00:04.33", "HIGH", "https://images.pexels.com/photos/10476388/pexels-photo-10476388.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"),
        ("EVT-003", "Zone Entry", 36, 177, "00:07.10", "HIGH", "https://images.pexels.com/photos/33610630/pexels-photo-33610630.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"),
    ]
    events = []
    for eid, etype, track_id, frame, ts, risk, default_url in raw_seeds:
        local_img = _find_evidence_file(eid, track_id, frame)
        events.append(IntrusionEvent(
            event_id=eid,
            event_type=etype,
            person_track_id=track_id,
            frame=frame,
            timestamp=ts,
            risk=risk,
            evidence_file=local_img or default_url,
            status="Confirmed",
            detection_method="Restricted Zone Entry",
            created_at=datetime.now().isoformat(),
        ))
    return events


def _try_supabase() -> list[IntrusionEvent] | None:
    """Attempt to fetch events from Supabase. Returns None if unavailable."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        return None
    try:
        from supabase import create_client
        client = create_client(SUPABASE_URL, SUPABASE_KEY)
        resp = client.table("intrusion_events").select("*").order("frame", ascending=True).execute()
        if not resp.data:
            return None
        events = []
        for row in resp.data:
            track_id = int(row.get("person_track_id", 0))
            frame = int(row.get("frame", 0))
            eid = str(row.get("event_id", ""))
            ev_file = row.get("evidence_file") or _find_evidence_file(eid, track_id, frame)
            events.append(IntrusionEvent(
                event_id=eid,
                event_type=row["event_type"],
                person_track_id=track_id,
                frame=frame,
                timestamp=row["timestamp"],
                risk=row["risk"],
                evidence_file=ev_file,
                status=row["status"],
                detection_method=row["detection_method"],
                created_at=row.get("created_at", ""),
            ))
        return events
    except Exception:
        return None


def _try_csv() -> list[IntrusionEvent] | None:
    """Attempt to read events from local CSV. Returns None if file missing."""
    abs_path = os.path.abspath(CSV_PATH)
    if not os.path.exists(abs_path):
        return None
    try:
        df = pd.read_csv(abs_path)
        events = []
        records = df.to_dict("records")
        for i, row in enumerate(records):
            track_id = int(row.get("person_track_id") if "person_track_id" in row and pd.notna(row.get("person_track_id")) else (row.get("Person ID", 0) if pd.notna(row.get("Person ID")) else 0))
            event_type = str(row.get("event_type") or row.get("Event") or "Zone Entry")
            frame = int(row.get("frame") if "frame" in row and pd.notna(row.get("frame")) else (row.get("Frame", 0) if pd.notna(row.get("Frame")) else 0))
            timestamp = str(row.get("timestamp") or row.get("Timestamp") or "00:00.00")
            risk = str(row.get("risk") or row.get("Risk") or "HIGH")
            event_id = str(row.get("event_id") or f"EVT-{i+1:03d}")
            status = str(row.get("status") or "Confirmed")
            detection_method = str(row.get("detection_method") or "Restricted Zone Entry")
            
            raw_ev = str(row.get("evidence_file", "")).strip()
            evidence_file = raw_ev if raw_ev and raw_ev != "nan" else _find_evidence_file(event_id, track_id, frame)
            
            events.append(IntrusionEvent(
                event_id=event_id,
                event_type=event_type,
                person_track_id=track_id,
                frame=frame,
                timestamp=timestamp,
                risk=risk,
                evidence_file=evidence_file,
                status=status,
                detection_method=detection_method,
                created_at=str(row.get("created_at") or datetime.now().isoformat()),
            ))
        return events
    except Exception:
        return None


try:
    import pymongo
    from pymongo import MongoClient
except ImportError:
    pymongo = None
    MongoClient = None

try:
    import certifi
except ImportError:
    certifi = None


def get_mongo_uri() -> str:
    try:
        if hasattr(st, "secrets"):
            for key in ["MONGODB_URI", "MONGO_URI", "MONGO_URL"]:
                try:
                    if key in st.secrets and st.secrets[key]:
                        val = str(st.secrets[key]).strip().strip("'\"")
                        if val:
                            return val
                except Exception:
                    pass
    except Exception:
        pass
    for key in ["MONGODB_URI", "MONGO_URI", "MONGO_URL"]:
        uri = os.environ.get(key, "").strip().strip("'\"")
        if uri:
            return uri
    return ""


MONGO_DB = "IBVAP"
MONGO_COLLECTION = "intrusion_events"


@st.cache_resource(ttl=3600, show_spinner=False)
def get_mongo_client(uri: str):
    if not uri or MongoClient is None:
        return None
    try:
        client_kwargs = {
            "tls": True,
            "serverSelectionTimeoutMS": 500,
            "connectTimeoutMS": 500,
            "socketTimeoutMS": 500,
        }
        if certifi is not None:
            client_kwargs["tlsCAFile"] = certifi.where()

        client = MongoClient(uri, **client_kwargs)
        client.admin.command("ping")
        return client
    except Exception as e:
        print("[ERROR] MongoDB connection error:", e)
        return None


def _try_mongodb() -> list[IntrusionEvent] | None:
    uri = get_mongo_uri()
    if not uri or MongoClient is None:
        return None
    client = get_mongo_client(uri)
    if client is None:
        return None
    try:
        db = client[MONGO_DB]
        collection = db[MONGO_COLLECTION]
        documents = list(collection.find({}, {"_id": 0}).sort("event_id", 1))
        if not documents:
            return None
        events = []
        for doc in documents:
            track_id = int(doc.get("person_track_id", 0))
            frame = int(doc.get("frame", 0))
            eid = str(doc.get("event_id") or "EVT-001")
            ev_file = doc.get("evidence_file") or _find_evidence_file(eid, track_id, frame)
            events.append(
                IntrusionEvent(
                    event_id=eid,
                    event_type=str(doc.get("event_type") or "Zone Entry"),
                    person_track_id=track_id,
                    frame=frame,
                    timestamp=str(doc.get("timestamp", "00:00.00")),
                    risk=str(doc.get("risk", "HIGH")),
                    evidence_file=ev_file,
                    status=str(doc.get("status", "Confirmed")),
                    detection_method=str(doc.get("detection_method", "Restricted Zone Entry")),
                    created_at=str(doc.get("created_at", datetime.now().isoformat()))
                )
            )
        return events
    except Exception:
        return None


@st.cache_data(ttl=300, show_spinner=False)
def fetch_events() -> list[IntrusionEvent]:
    """Fetch intrusion events: MongoDB -> Supabase -> CSV -> seed data."""
    for loader in (_try_mongodb, _try_supabase, _try_csv):
        result = loader()
        if result:
            return result
    return _seed_events()


@st.cache_data(ttl=300, show_spinner=False)
def get_video_path() -> str | None:
    abs_path = os.path.abspath(VIDEO_PATH)
    return abs_path if os.path.exists(abs_path) else None


def get_system_status() -> dict:
    return {
        "ai_detection": True,
        "object_tracking": True,
        "zone_monitoring": True,
        "event_logger": True,
        "evidence_capture": True,
        "audit_system": True,
    }


def timestamp_to_seconds(ts: str) -> float:
    parts = ts.split(":")
    minutes = int(parts[0]) if len(parts) > 1 else 0
    seconds = float(parts[-1]) if parts else 0.0
    return minutes * 60 + seconds


def events_to_csv(events: list[IntrusionEvent]) -> str:
    df = pd.DataFrame([e.to_dict() for e in events])
    output = io.StringIO()
    df.to_csv(output, index=False)
    return output.getvalue()
