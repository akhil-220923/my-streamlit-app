"""
IBVAP — Intelligent Border Video Analytics Platform
AI-Powered Border Surveillance, Intrusion Detection & Security Analytics
SIH 2026 — Blockchain & Cybersecurity

Single-file Streamlit application.
Install: pip install streamlit pandas plotly Pillow requests supabase pymongo certifi python-dotenv
Run:     streamlit run app.py
"""
import os
import io
import json
import hashlib
from dataclasses import dataclass, asdict
from typing import Optional
from datetime import datetime

import pandas as pd
import streamlit as st

try:
    import plotly.express as px
except ImportError:
    px = None

try:
    import requests
    from PIL import Image
    from io import BytesIO
    HAS_IMAGE_LIBS = True
except ImportError:
    HAS_IMAGE_LIBS = False

try:
    import pymongo
    from pymongo import MongoClient
    from pymongo.server_api import ServerApi
except ImportError:
    pymongo = None
    MongoClient = None
    ServerApi = None

try:
    import certifi
    HAS_CERTIFI = True
except ImportError:
    certifi = None
    HAS_CERTIFI = False

try:
    from dotenv import load_dotenv
    load_dotenv()
    load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
except Exception:
    pass


# ═══════════════════════════════════════════════════════════════════════════
# DATA LAYER
# ═══════════════════════════════════════════════════════════════════════════

SUPABASE_URL = os.environ.get("SUPABASE_URL") or os.environ.get("VITE_SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_ANON_KEY") or os.environ.get("VITE_SUPABASE_ANON_KEY", "")

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

OUTPUT_DIR = os.path.join(PROJECT_ROOT, "output")

CSV_PATH = os.path.join(
    OUTPUT_DIR,
    "intrusion_log.csv"
)

VIDEO_PATH = os.path.join(
    OUTPUT_DIR,
    "final_intrusion_video.mp4"
)

EVIDENCE_DIR = os.path.join(
    OUTPUT_DIR,
    "evidence"
)

def get_mongo_uri():
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

MONGO_URI = get_mongo_uri()
MONGO_DB = "IBVAP"
MONGO_COLLECTION = "intrusion_events"


SECURE_LOG_PATH = os.path.join(
    OUTPUT_DIR,
    "secure_audit_log.csv"
)

ROOT_HASH_PATH = os.path.join(
    OUTPUT_DIR,
    "audit_root_hash.txt"
)

BLOCKCHAIN_PATH = os.path.join(
    OUTPUT_DIR,
    "blockchain_ledger.json"
)


@st.cache_resource(ttl=3600, show_spinner=False)
def get_mongo_client(uri: str):
    if not uri or MongoClient is None:
        return None
    try:
        client_kwargs = {
            "tls": True,
            "serverSelectionTimeoutMS": 3000,
            "connectTimeoutMS": 3000,
            "socketTimeoutMS": 3000,
        }
        if certifi is not None:
            client_kwargs["tlsCAFile"] = certifi.where()

        client = MongoClient(uri, **client_kwargs)
        client.admin.command("ping")
        print("[OK] MongoDB ping successful")
        return client
    except Exception as e:
        print("[ERROR] MongoDB connection error:", e)
        return None


def get_mongo_collection():
    uri = get_mongo_uri()
    print("MONGODB_URI configured:", bool(uri))

    if not uri:
        print("[ERROR] MONGODB_URI is empty")
        return None

    if MongoClient is None:
        print("[ERROR] PyMongo is not installed")
        return None

    client = get_mongo_client(uri)
    if client is None:
        return None

    try:
        db = client[MONGO_DB]
        collection = db[MONGO_COLLECTION]
        print("[OK] MongoDB collection connected")
        return collection

    except Exception as e:
        print("[ERROR] MongoDB collection error:", e)
        return None


@dataclass
class IntrusionEvent:
    event_id: str
    event_type: str
    person_track_id: int
    frame: int
    timestamp: str
    risk: str
    evidence_file: Optional[str] = None
    status: str = "Confirmed"
    detection_method: str = "Restricted Zone Entry"
    created_at: str = ""

    def to_dict(self):
        return asdict(self)


def _seed_events():
    return [
        IntrusionEvent("EVT-001", "Zone Entry", 2, 30, "00:01.20", "HIGH",
            "https://images.pexels.com/photos/13530045/pexels-photo-13530045.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
            "Confirmed", "Restricted Zone Entry", datetime.now().isoformat()),
        IntrusionEvent("EVT-002", "Zone Entry", 7, 108, "00:04.33", "HIGH",
            "https://images.pexels.com/photos/10476388/pexels-photo-10476388.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
            "Confirmed", "Restricted Zone Entry", datetime.now().isoformat()),
        IntrusionEvent("EVT-003", "Zone Entry", 36, 177, "00:07.10", "HIGH",
            "https://images.pexels.com/photos/33610630/pexels-photo-33610630.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
            "Confirmed", "Restricted Zone Entry", datetime.now().isoformat()),
    ]


def _try_supabase():
    if not SUPABASE_URL or not SUPABASE_KEY:
        return None
    try:
        from supabase import create_client
        client = create_client(SUPABASE_URL, SUPABASE_KEY)
        resp = client.table("intrusion_events").select("*").order("frame", desc=False).execute()
        if not resp.data:
            return None
        events = []
        for row in resp.data:
            events.append(IntrusionEvent(
                row["event_id"], row["event_type"], row["person_track_id"],
                row["frame"], row["timestamp"], row["risk"], row.get("evidence_file"),
                row["status"], row["detection_method"], row.get("created_at", "")))
        return events
    except Exception:
        return None


def save_events_to_mongodb(events):
    """Save or update intrusion events to MongoDB Atlas collection."""
    try:
        collection = get_mongo_collection()
        if collection is None or not events:
            return False
        saved_count = 0
        for event in events:
            doc = event.to_dict()
            collection.update_one(
                {"event_id": event.event_id},
                {"$set": doc},
                upsert=True
            )
            saved_count += 1
        print(f"[OK] Saved/Synced {saved_count} events to MongoDB Atlas")
        return True
    except Exception as e:
        print("[WARN] MongoDB sync skipped:", e)
        return False


def _try_mongodb():
    """Load intrusion events from MongoDB."""
    collection = get_mongo_collection()
    if collection is None:
        print("[ERROR] MongoDB collection is None")
        return None

    try:
        documents = list(
            collection.find(
                {},
                {"_id": 0}
            ).sort("event_id", 1)
        )

        print("[OK] MongoDB documents found:", len(documents))
        if not documents:
            print("[WARN] MongoDB collection is empty")
            return None

        events = []
        for doc in documents:
            event_id = str(doc.get("event_id") or doc.get("eventId") or doc.get("id") or "")
            event_type = str(doc.get("event_type") or doc.get("eventType") or doc.get("type") or "Zone Entry")

            try:
                person_track_id = int(doc.get("person_track_id") if doc.get("person_track_id") is not None else doc.get("personTrackId") if doc.get("personTrackId") is not None else doc.get("track_id") if doc.get("track_id") is not None else doc.get("person_id", 0))
            except Exception:
                person_track_id = 0

            try:
                frame = int(doc.get("frame") if doc.get("frame") is not None else doc.get("frame_number", 0))
            except Exception:
                frame = 0

            timestamp = str(doc.get("timestamp") or doc.get("time") or "00:00.00").strip()
            risk = str(doc.get("risk") or doc.get("risk_level") or "HIGH").strip()

            evidence_file = doc.get("evidence_file") or doc.get("evidenceFile") or doc.get("evidence") or doc.get("evidence_url") or doc.get("image")
            evidence_file_str = str(evidence_file) if evidence_file else None

            status = str(doc.get("status") or "Confirmed")
            detection_method = str(doc.get("detection_method") or doc.get("detectionMethod") or doc.get("method") or "Restricted Zone Entry")
            created_at = str(doc.get("created_at") or doc.get("createdAt") or datetime.now().isoformat())

            events.append(
                IntrusionEvent(
                    event_id=event_id,
                    event_type=event_type,
                    person_track_id=person_track_id,
                    frame=frame,
                    timestamp=timestamp,
                    risk=risk,
                    evidence_file=evidence_file_str,
                    status=status,
                    detection_method=detection_method,
                    created_at=created_at
                )
            )

        return events

    except Exception as e:
        print("[ERROR] MongoDB error:", e)
        return None


def _try_csv():
    abs_path = os.path.abspath(CSV_PATH)
    if not os.path.exists(abs_path):
        return None

    try:
        df = pd.read_csv(abs_path)
        print("IBVAP CSV columns:", list(df.columns))

        events = []
        records = df.to_dict("records")
        for index, row in enumerate(records):
            event_id = f"EVT-{index + 1:03d}"
            event_type = str(row.get("Event", row.get("event_type", "Zone Entry"))).strip()

            track_value = row.get("Person ID", row.get("person_track_id", 0))
            try:
                person_track_id = int(float(track_value))
            except Exception:
                person_track_id = 0

            frame_value = row.get("Frame", row.get("frame", 0))
            try:
                frame = int(float(frame_value))
            except Exception:
                frame = 0

            timestamp = str(row.get("Timestamp", row.get("timestamp", "00:00.00"))).strip()
            risk = str(row.get("Risk", row.get("risk", "HIGH"))).strip()
            status = str(row.get("status", "Confirmed"))
            detection_method = str(row.get("detection_method", "Restricted Zone Entry"))
            created_at = datetime.now().isoformat()

            evidence_file = os.path.join(
                EVIDENCE_DIR,
                f"{event_id}_track_{person_track_id}_frame_{frame}.jpg"
            )
            if not os.path.exists(evidence_file):
                evidence_file = None

            events.append(
                IntrusionEvent(
                    event_id,
                    event_type,
                    person_track_id,
                    frame,
                    timestamp,
                    risk,
                    evidence_file,
                    status,
                    detection_method,
                    created_at
                )
            )

        return events

    except Exception as e:
        print("IBVAP CSV error:", e)
        return None


@st.cache_data(ttl=60, show_spinner=False)
def fetch_events():
    print("========== FETCH EVENTS ==========")
    events = _try_mongodb()

    if events:
        print("[OK] SOURCE = MONGODB")
        return events

    print("[WARN] MongoDB failed or empty, trying CSV")
    events = _try_csv()

    if events:
        print("[WARN] SOURCE = CSV")
        return events

    print("[WARN] SOURCE = SEED DATA")
    seed_evts = _seed_events()
    return seed_evts


@st.cache_data(ttl=300, show_spinner=False)
def get_video_path():
    abs_path = os.path.abspath(VIDEO_PATH)
    return abs_path if os.path.exists(abs_path) else None


@st.cache_data(ttl=60, show_spinner=False)
def verify_secure_audit_log():
    """Verify the SHA-256 hash chain stored in secure_audit_log.csv."""
    if not os.path.exists(SECURE_LOG_PATH):
        return False, "Secure audit log not found", 0

    if not os.path.exists(ROOT_HASH_PATH):
        return False, "Audit root hash not found", 0

    try:
        df = pd.read_csv(SECURE_LOG_PATH)

        with open(ROOT_HASH_PATH, "r") as f:
            expected_root_hash = f.read().strip()

        previous_hash = "GENESIS"
        for _, row in df.iterrows():
            record = {
                "event_id": str(row["event_id"]),
                "event_type": str(row["event_type"]),
                "person_track_id": int(row["person_track_id"]),
                "frame": int(row["frame"]),
                "timestamp": str(row["timestamp"]),
                "risk": str(row["risk"]),
            }

            record_string = json.dumps(record, sort_keys=True, separators=(",", ":"))
            hash_input = previous_hash + record_string
            calculated_hash = hashlib.sha256(hash_input.encode("utf-8")).hexdigest()

            if str(row["previous_hash"]) != previous_hash:
                return False, f"Chain broken at {row['event_id']}", 0

            if str(row["record_hash"]) != calculated_hash:
                return False, f"Record modified: {row['event_id']}", 0

            previous_hash = calculated_hash

        if previous_hash != expected_root_hash:
            return False, "Root hash mismatch", 0

        return True, "Audit log integrity verified successfully", len(df)

    except Exception as e:
        return False, f"Verification error: {e}", 0


def create_blockchain_ledger():
    """Create a local tamper-evident blockchain-style audit ledger."""
    if not os.path.exists(SECURE_LOG_PATH):
        return False, "Secure audit log not found"

    try:
        df = pd.read_csv(SECURE_LOG_PATH)
        blocks = []

        genesis_data = {
            "type": "GENESIS",
            "system": "IBVAP",
            "description": "IBVAP Audit Blockchain Genesis Block"
        }
        genesis_payload = {
            "block_index": 0,
            "data": genesis_data,
            "previous_hash": "0" * 64
        }
        genesis_string = json.dumps(genesis_payload, sort_keys=True, separators=(",", ":"))
        genesis_hash = hashlib.sha256(genesis_string.encode("utf-8")).hexdigest()

        blocks.append({
            "block_index": 0,
            "timestamp": datetime.now().isoformat(),
            "data": genesis_data,
            "previous_hash": "0" * 64,
            "block_hash": genesis_hash
        })

        previous_hash = genesis_hash

        for index, row in df.iterrows():
            event_data = {
                "event_id": str(row["event_id"]),
                "event_type": str(row["event_type"]),
                "person_track_id": int(row["person_track_id"]),
                "frame": int(row["frame"]),
                "timestamp": str(row["timestamp"]),
                "risk": str(row["risk"])
            }
            block_payload = {
                "block_index": index + 1,
                "data": event_data,
                "previous_hash": previous_hash
            }
            block_string = json.dumps(block_payload, sort_keys=True, separators=(",", ":"))
            block_hash = hashlib.sha256(block_string.encode("utf-8")).hexdigest()

            blocks.append({
                "block_index": index + 1,
                "timestamp": datetime.now().isoformat(),
                "data": event_data,
                "previous_hash": previous_hash,
                "block_hash": block_hash
            })
            previous_hash = block_hash

        ledger = {
            "network": "IBVAP-LOCAL-AUDIT-LEDGER",
            "algorithm": "SHA-256",
            "block_count": len(blocks),
            "created_at": datetime.now().isoformat(),
            "blocks": blocks
        }

        with open(BLOCKCHAIN_PATH, "w") as f:
            json.dump(ledger, f, indent=2)

        return True, f"{len(blocks)} blocks created"

    except Exception as e:
        return False, str(e)


@st.cache_data(ttl=60, show_spinner=False)
def verify_blockchain_ledger():
    """Verify the complete blockchain audit ledger."""
    if not os.path.exists(BLOCKCHAIN_PATH):
        return False, "Blockchain ledger not found", 0

    try:
        with open(BLOCKCHAIN_PATH, "r") as f:
            ledger = json.load(f)

        blocks = ledger.get("blocks", [])
        if not blocks:
            return False, "No blocks found", 0

        previous_hash = "0" * 64
        for block in blocks:
            block_payload = {
                "block_index": block["block_index"],
                "data": block["data"],
                "previous_hash": block["previous_hash"]
            }
            block_string = json.dumps(block_payload, sort_keys=True, separators=(",", ":"))
            calculated_hash = hashlib.sha256(block_string.encode("utf-8")).hexdigest()

            if block["previous_hash"] != previous_hash:
                return False, f"Chain broken at block {block['block_index']}", 0

            if block["block_hash"] != calculated_hash:
                return False, f"Block modified: {block['block_index']}", 0

            previous_hash = block["block_hash"]

        return True, "Blockchain audit ledger verified successfully", len(blocks)

    except Exception as e:
        return False, f"Verification error: {e}", 0


def get_system_status():
    return {"ai_detection": True, "object_tracking": True, "zone_monitoring": True,
            "event_logger": True, "evidence_capture": True, "audit_system": True}


@st.cache_data(ttl=3600, show_spinner=False)
def events_to_csv(events):
    df = pd.DataFrame([e.to_dict() for e in events])
    output = io.StringIO()
    df.to_csv(output, index=False)
    return output.getvalue()


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_image_bytes(source):
    """Load evidence image from a local file or remote URL."""
    if source.startswith(("http://", "https://")):
        response = requests.get(source, timeout=3)
        response.raise_for_status()
        return response.content

    with open(source, "rb") as f:
        return f.read()


# ═══════════════════════════════════════════════════════════════════════════
# UI COMPONENTS & MODERN ICONS
# ═══════════════════════════════════════════════════════════════════════════

def get_icon_svg(name, color="currentColor", size=18):
    """Return crisp modern SVG icons for UI elements."""
    icons = {
        "command-center": f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="7" height="9" x="3" y="3" rx="1"/><rect width="7" height="5" x="14" y="3" rx="1"/><rect width="7" height="9" x="14" y="12" rx="1"/><rect width="7" height="5" x="3" y="16" rx="1"/></svg>',
        "surveillance": f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m16 13 5.223 3.482a.5.5 0 0 0 .777-.416V7.934a.5.5 0 0 0-.777-.416L16 11"/><rect width="13" height="10" x="3" y="7" rx="2"/></svg>',
        "security-events": f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><line x1="12" x2="12" y1="9" y2="13"/><line x1="12" x2="12.01" y1="17" y2="17"/></svg>',
        "digital-evidence": f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14.5 4h-5L7 7H4a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-3l-2.5-3z"/><circle cx="12" cy="13" r="3"/></svg>',
        "audit-log": f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10"/><path d="m9 12 2 2 4-4"/></svg>',
        "system": f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.38a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"/><circle cx="12" cy="12" r="3"/></svg>',
        "sun": f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2"/><path d="M12 20v2"/><path d="m4.93 4.93 1.41 1.41"/><path d="m17.66 17.66 1.41 1.41"/><path d="M2 12h2"/><path d="M20 12h2"/><path d="m6.34 17.66-1.41 1.41"/><path d="m19.07 4.93-1.41 1.41"/></svg>',
        "moon": f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/></svg>',
        "sidebar-toggle": f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="18" height="18" x="3" y="3" rx="2"/><path d="M9 3v18"/><path d="m14 9 3 3-3 3"/></svg>',
        "radar": f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19.07 4.93A10 10 0 0 0 6.99 3.34"/><path d="M4.93 19.07A10 10 0 0 0 17.01 20.66"/><path d="M2 12h20"/><path d="M12 2v20"/><path d="m12 12 5-5"/><circle cx="12" cy="12" r="2"/></svg>',
        "users": f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>',
        "flame": f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 0 0 2.5 2.5z"/></svg>',
        "camera": f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14.5 4h-5L7 7H4a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-3l-2.5-3z"/><circle cx="12" cy="13" r="3"/></svg>',
        "shield": f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.8 17 5 19 5a1 1 0 0 1 1 1z"/></svg>',
        "check-circle": f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>'
    }
    return icons.get(name, f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2"><circle cx="12" cy="12" r="10"/></svg>')


def risk_badge(risk):
    colors = {
        "HIGH": ("rgba(255, 59, 92, 0.15)", "#ff3b5c", "rgba(255, 59, 92, 0.35)"),
        "MEDIUM": ("rgba(245, 158, 11, 0.15)", "#f59e0b", "rgba(245, 158, 11, 0.35)"),
        "LOW": ("rgba(0, 245, 212, 0.15)", "#00f5d4", "rgba(0, 245, 212, 0.35)")
    }
    bg, text, border = colors.get(risk, colors["LOW"])
    dot = f'<span style="display:inline-block;width:7px;height:7px;border-radius:50%;background:{text};margin-right:6px;box-shadow: 0 0 8px {text};"></span>'
    return f'<span style="background:{bg};color:{text};border:1px solid {border};padding:4px 12px;border-radius:20px;font-size:11px;font-weight:700;display:inline-flex;align-items:center;letter-spacing:0.5px;">{dot}{risk}</span>'


def status_indicator(online, label=""):
    color = "#00f5d4" if online else "#ff3b5c"
    dot = f'<span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:{color};margin-right:6px;box-shadow:0 0 10px {color};animation: pulseDot 2s infinite;"></span>'
    if label:
        text_color = "#00f5d4" if online else "#ff3b5c"
        return f'{dot}<span style="font-size:12px;font-weight:700;color:{text_color};letter-spacing:0.5px;">{label}</span>'
    return dot


def metric_card_html(label, value, icon_key, accent="teal"):
    theme = st.session_state.get("ibvap_theme", "dark")
    accent_dark = {
        "teal": ("rgba(0,245,212,0.15)", "#00f5d4", "rgba(0,245,212,0.3)"),
        "red": ("rgba(255,59,92,0.15)", "#ff3b5c", "rgba(255,59,92,0.3)"),
        "amber": ("rgba(245,158,11,0.15)", "#f59e0b", "rgba(245,158,11,0.3)"),
        "green": ("rgba(16,185,129,0.15)", "#10b981", "rgba(16,185,129,0.3)"),
        "navy": ("rgba(56,189,248,0.15)", "#38bdf8", "rgba(56,189,248,0.3)")
    }
    accent_light = {
        "teal": ("#f0fdfa", "#0d9488", "#cbd5e1"),
        "red": ("#fef2f2", "#dc2626", "#cbd5e1"),
        "amber": ("#fffbeb", "#d97706", "#cbd5e1"),
        "green": ("#f0fdf4", "#16a34a", "#cbd5e1"),
        "navy": ("#f0f9ff", "#0284c7", "#cbd5e1")
    }
    accent_map = accent_dark if theme == "dark" else accent_light
    bg, text, border_glow = accent_map.get(accent, accent_map["teal"])
    icon_svg = get_icon_svg(icon_key, color=text, size=22)

    card_bg = "linear-gradient(145deg, #0e1726 0%, #131f37 100%)" if theme == "dark" else "#ffffff"
    border_col = "rgba(255,255,255,0.08)" if theme == "dark" else "#e2e8f0"
    val_col = "#ffffff" if theme == "dark" else "#0f172a"
    lbl_col = "#94a3b8" if theme == "dark" else "#64748b"

    return f"""
    <div style="background:{card_bg};border:1px solid {border_col};border-radius:16px;padding:22px;box-shadow:0 8px 32px rgba(0,0,0,0.18);transition:all 0.3s cubic-bezier(0.4, 0, 0.2, 1);position:relative;overflow:hidden;">
        <div style="position:absolute;top:-20px;right:-20px;width:80px;height:80px;border-radius:50%;background:{bg};filter:blur(24px);pointer-events:none;"></div>
        <div style="display:flex;align-items:center;justify-space-between;margin-bottom:14px;">
            <div style="width:46px;height:46px;border-radius:12px;background:{bg};border:1px solid {border_glow};display:flex;align-items:center;justify-content:center;color:{text};box-shadow:0 4px 14px {bg};">{icon_svg}</div>
        </div>
        <p style="font-size:30px;font-weight:800;color:{val_col};margin:0;line-height:1.2;letter-spacing:-0.5px;">{value}</p>
        <p style="font-size:12px;font-weight:600;color:{lbl_col};margin:6px 0 0 0;text-transform:uppercase;letter-spacing:0.5px;">{label}</p>
    </div>"""


def pipeline_step_html(icon_key, label, desc, is_last=False):
    theme = st.session_state.get("ibvap_theme", "dark")
    bg = "#131f37" if theme == "dark" else "#f8fafc"
    border = "rgba(255,255,255,0.08)" if theme == "dark" else "#e2e8f0"
    title_col = "#f8fafc" if theme == "dark" else "#1e293b"
    desc_col = "#94a3b8" if theme == "dark" else "#64748b"
    icon_svg = get_icon_svg(icon_key, color="#00f5d4" if theme == "dark" else "#0d9488", size=18)
    arrow = "" if is_last else f'<div style="text-align:center;color:#64748b;font-size:14px;padding:4px 0;">&darr;</div>'

    return f"""
    <div style="display:flex;align-items:center;gap:12px;padding:12px 16px;background:{bg};border:1px solid {border};border-radius:12px;margin-bottom:4px;box-shadow:0 2px 10px rgba(0,0,0,0.1);">
        <div style="width:36px;height:36px;border-radius:10px;background:rgba(0,245,212,0.1);border:1px solid rgba(0,245,212,0.2);display:flex;align-items:center;justify-content:center;flex-shrink:0;">{icon_svg}</div>
        <div><div style="font-size:13px;font-weight:700;color:{title_col};">{label}</div>
        <div style="font-size:11px;color:{desc_col};">{desc}</div></div>
    </div>{arrow}"""


def security_pipeline_html():
    steps = [
        ("surveillance", "Video Input", "Surveillance feed"),
        ("radar", "YOLO11 Detection", "Person detection"),
        ("users", "ByteTrack Tracking", "Multi-object tracking"),
        ("radar", "Zone Analysis", "Restricted zone check"),
        ("security-events", "Intrusion Detection", "Zone entry event"),
        ("command-center", "Timestamp", "Frame & time"),
        ("flame", "Risk Classification", "HIGH / MEDIUM / LOW"),
        ("digital-evidence", "Evidence Capture", "Visual snapshot"),
        ("audit-log", "Audit Log", "Structured record"),
    ]
    theme = st.session_state.get("ibvap_theme", "dark")
    heading_col = "#f8fafc" if theme == "dark" else "#1e293b"
    parts = [f'<div style="font-size:15px;font-weight:800;color:{heading_col};margin-bottom:14px;display:flex;align-items:center;gap:10px;">{get_icon_svg("shield", color="#00f5d4", size=22)} AI Security Pipeline</div>']
    for i, (icon_key, label, desc) in enumerate(steps):
        parts.append(pipeline_step_html(icon_key, label, desc, is_last=(i == len(steps) - 1)))
    return "".join(parts)


def empty_state_html(icon_key, title, description):
    theme = st.session_state.get("ibvap_theme", "dark")
    title_col = "#f8fafc" if theme == "dark" else "#1e293b"
    desc_col = "#94a3b8" if theme == "dark" else "#64748b"
    icon_svg = get_icon_svg(icon_key, color="#00f5d4" if theme == "dark" else "#0d9488", size=32)
    return f"""
    <div style="text-align:center;padding:48px 20px;">
        <div style="width:68px;height:68px;border-radius:18px;background:rgba(0,245,212,0.1);border:1px solid rgba(0,245,212,0.2);display:flex;align-items:center;justify-content:center;margin:0 auto 16px;">{icon_svg}</div>
        <h3 style="font-size:17px;font-weight:700;color:{title_col};margin:0 0 6px 0;">{title}</h3>
        <p style="font-size:13px;color:{desc_col};max-width:420px;margin:0 auto;line-height:1.5;">{description}</p>
    </div>"""


def section_header(title, subtitle="", icon_key=None):
    theme = st.session_state.get("ibvap_theme", "dark")
    title_col = "#ffffff" if theme == "dark" else "#0f172a"
    sub_col = "#94a3b8" if theme == "dark" else "#64748b"
    icon_html = f'<span style="display:inline-flex;align-items:center;margin-right:10px;">{get_icon_svg(icon_key, color="#00f5d4" if theme=="dark" else "#0d9488", size=24)}</span>' if icon_key else ""
    sub = f'<p style="font-size:13px;color:{sub_col};margin:4px 0 0 0;font-weight:500;">{subtitle}</p>' if subtitle else ""
    return f'<div style="margin-bottom:22px;display:flex;align-items:flex-start;gap:4px;"><div><h2 style="font-size:24px;font-weight:800;color:{title_col};margin:0;display:flex;align-items:center;letter-spacing:-0.5px;">{icon_html}{title}</h2>{sub}</div></div>'


# ═══════════════════════════════════════════════════════════════════════════
# PAGE: COMMAND CENTER
# ═══════════════════════════════════════════════════════════════════════════

@st.cache_data(ttl=60, show_spinner=False)
def _build_risk_chart(events_tuples):
    if not px or not events_tuples:
        return None
    risk_counts = pd.DataFrame([{"Risk": r, "Count": 1} for _, r, _ in events_tuples]).groupby("Risk").sum().reset_index()
    fig = px.bar(
        risk_counts, x="Risk", y="Count", color="Risk",
        color_discrete_map={"HIGH": "#ff3b5c", "MEDIUM": "#f59e0b", "LOW": "#00f5d4"},
        title="Risk Level Distribution"
    )
    fig.update_layout(
        height=280, margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(size=12, color="#94a3b8")
    )
    return fig


@st.cache_data(ttl=60, show_spinner=False)
def _build_timeline_chart(events_tuples):
    if not px or not events_tuples:
        return None
    timeline_df = pd.DataFrame([{"Frame": f, "Track": str(t), "Risk": r} for f, t, r in events_tuples])
    fig2 = px.scatter(
        timeline_df, x="Frame", y="Track", color="Risk",
        color_discrete_map={"HIGH": "#ff3b5c", "MEDIUM": "#f59e0b", "LOW": "#00f5d4"},
        title="Intrusion Events Across Frames"
    )
    fig2.update_traces(marker_size=14)
    fig2.update_layout(
        height=280, margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(size=12, color="#94a3b8")
    )
    return fig2


def render_command_center(events):
    st.markdown(section_header("Command Center", "Executive security overview & AI operations", icon_key="command-center"), unsafe_allow_html=True)

    unique_tracks = len(set(e.person_track_id for e in events))
    evidence_count = sum(1 for e in events if e.evidence_file)
    threat_level = "HIGH" if events else "NORMAL"

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(metric_card_html("Intrusion Events", str(len(events)), "security-events", "red"), unsafe_allow_html=True)
    with col2:
        st.markdown(metric_card_html("Unique Person Tracks", str(unique_tracks), "users", "navy"), unsafe_allow_html=True)
    with col3:
        st.markdown(metric_card_html("Threat Level", threat_level, "flame", "red" if threat_level == "HIGH" else "green"), unsafe_allow_html=True)
    with col4:
        st.markdown(metric_card_html("Evidence Captured", str(evidence_count), "digital-evidence", "teal"), unsafe_allow_html=True)

    st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)

    col_left, col_right = st.columns(2)

    with col_left:
        if events:
            st.markdown(f"""
            <div class="ibvap-card ibvap-card-threat">
                <div style="display:flex;align-items:flex-start;gap:16px;">
                    <div style="width:52px;height:52px;border-radius:14px;background:rgba(255,59,92,0.2);
                    border:1px solid rgba(255,59,92,0.4);display:flex;align-items:center;justify-content:center;
                    font-size:22px;font-weight:800;color:#ff3b5c;flex-shrink:0;box-shadow:0 0 16px rgba(255,59,92,0.3);">!</div>
                    <div>
                        <h3 style="color:#ff3b5c;font-size:16px;font-weight:800;margin:0;letter-spacing:-0.3px;">HIGH RISK ACTIVITY DETECTED</h3>
                        <p style="font-size:13px;color:#94a3b8;margin:6px 0 0 0;line-height:1.5;">{len(events)} intrusion event{'s' if len(events) != 1 else ''} recorded in restricted zone.</p>
                    </div>
                </div>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="ibvap-card ibvap-card-secure">
                <div style="display:flex;align-items:flex-start;gap:16px;">
                    <div style="width:52px;height:52px;border-radius:14px;background:rgba(16,185,129,0.2);
                    border:1px solid rgba(16,185,129,0.4);display:flex;align-items:center;justify-content:center;
                    font-size:18px;font-weight:800;color:#10b981;flex-shrink:0;box-shadow:0 0 16px rgba(16,185,129,0.3);">OK</div>
                    <div>
                        <h3 style="color:#10b981;font-size:16px;font-weight:800;margin:0;letter-spacing:-0.3px;">SYSTEM SECURE</h3>
                        <p style="font-size:13px;color:#94a3b8;margin:6px 0 0 0;line-height:1.5;">No active intrusion detected. All perimeter zones monitored.</p>
                    </div>
                </div>
            </div>""", unsafe_allow_html=True)

    with col_right:
        modules = [
            ("AI", "AI Detection", "YOLO11"), ("TRK", "Object Tracking", "ByteTrack"),
            ("ZN", "Restricted Zone Monitoring", "Polygon zone"), ("LOG", "Event Logger", "Structured log"),
            ("EVD", "Evidence Capture", "Visual snapshot"), ("SEC", "Audit System", "CSV audit trail"),
        ]
        items_html = ""
        for icon, label, sub in modules:
            items_html += f"""<div class="health-item"><div class="health-item-icon">{icon}</div>
            <div style="flex:1;min-width:0;"><div class="health-item-label">{label}</div>
            <div class="health-item-sub">{sub}</div></div>{status_indicator(True, "ONLINE")}</div>"""
        st.markdown(f"""<div class="ibvap-card"><div style="display:flex;align-items:center;
        justify-content:space-between;margin-bottom:14px;"><h3 style="margin:0;">System Health Status</h3>
        <span style="font-size:12px;font-weight:700;color:#00f5d4;letter-spacing:0.5px;">All Systems Operational</span></div>
        <div class="health-grid">{items_html}</div></div>""", unsafe_allow_html=True)

    st.markdown(f'<div class="pipeline-container">{security_pipeline_html()}</div>', unsafe_allow_html=True)

    if events and px:
        events_tuples = tuple((e.frame, e.person_track_id, e.risk) for e in events)
        fig1 = _build_risk_chart(events_tuples)
        fig2 = _build_timeline_chart(events_tuples)

        if fig1 and fig2:
            st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)
            col_chart1, col_chart2 = st.columns(2)
            with col_chart1:
                st.plotly_chart(fig1, width="stretch")
            with col_chart2:
                st.plotly_chart(fig2, width="stretch")

    st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)
    st.markdown("""<div class="ibvap-card"><div style="display:flex;align-items:center;
    justify-content:space-between;margin-bottom:14px;"><h3 style="margin:0;">Recent Security Events</h3></div>""", unsafe_allow_html=True)
    if not events:
        st.markdown('<p style="text-align:center;color:#94a3b8;padding:24px;">No intrusion events detected. Surveillance system is operating normally.</p>', unsafe_allow_html=True)
    else:
        for event in events[:5]:
            st.markdown(f"""<div class="event-item"><div style="display:flex;align-items:center;gap:14px;">
            <div style="width:36px;height:36px;border-radius:10px;background:rgba(255,59,92,0.15);border:1px solid rgba(255,59,92,0.3);display:flex;align-items:center;
            justify-content:center;font-size:16px;font-weight:800;color:#ff3b5c;">!</div><div><div style="font-size:13px;font-weight:700;color:#f8fafc;">{event.event_type}</div>
            <div style="font-size:11px;color:#94a3b8;">Track {event.person_track_id} — Frame {event.frame} — {event.timestamp}</div></div></div>
            {risk_badge(event.risk)}</div>""", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# PAGE: SURVEILLANCE
# ═══════════════════════════════════════════════════════════════════════════

def render_surveillance(events):
    st.markdown(section_header("Surveillance", "Border surveillance monitoring & video stream analysis"), unsafe_allow_html=True)
    video_path = get_video_path()
    col_video, col_zone = st.columns([2, 1])

    with col_video:
        st.markdown("""<div class="ibvap-card" style="padding:0;overflow:hidden;">
        <div style="display:flex;align-items:center;justify-content:space-between;padding:14px 18px;
        border-bottom:1px solid rgba(255,255,255,0.08);background:rgba(14,23,38,0.8);">
        <div style="display:flex;align-items:center;gap:10px;"><span style="font-size:11px;font-weight:800;color:#00f5d4;letter-spacing:0.5px;">FEED</span>
        <span style="font-size:14px;font-weight:700;color:#f8fafc;">Border Surveillance Camera</span>
        <span style="font-size:12px;color:#94a3b8;font-family:monospace;">CAM-01</span></div>
        <div style="display:flex;align-items:center;gap:6px;">
        <span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:#00f5d4;box-shadow:0 0 8px #00f5d4;"></span>
        <span style="font-size:12px;font-weight:700;color:#00f5d4;">PROCESSED</span></div></div></div>""", unsafe_allow_html=True)

        if video_path:
            st.video(video_path)
        else:
            st.markdown("""<div style="background:#09101d;aspect-ratio:16/9;border-radius:0 0 14px 14px;position:relative;overflow:hidden;border:1px solid rgba(255,255,255,0.08);">
            <div style="position:absolute;inset:0;opacity:0.15;background-image:linear-gradient(rgba(0,245,212,0.3) 1px,transparent 1px),linear-gradient(90deg,rgba(0,245,212,0.3) 1px,transparent 1px);background-size:40px 40px;"></div>
            <svg style="position:absolute;inset:0;width:100%;height:100%;" preserveAspectRatio="none" viewBox="0 0 100 56">
            <polygon points="30,20 70,20 75,45 25,45" fill="rgba(255,59,92,0.08)" stroke="rgba(255,59,92,0.6)" stroke-width="0.4" stroke-dasharray="1,1"/>
            <text x="50" y="36" fill="rgba(255,59,92,0.8)" font-size="2.2" text-anchor="middle" font-family="monospace">RESTRICTED ZONE</text></svg>
            <div style="position:absolute;top:30%;left:35%;width:64px;height:96px;border:2px solid rgba(0,245,212,0.7);border-radius:4px;">
            <span style="position:absolute;top:-20px;left:0;font-size:10px;font-family:monospace;color:#00f5d4;background:rgba(9,16,29,0.9);padding:1px 4px;border-radius:2px;">ID:2</span></div>
            <div style="position:absolute;top:45%;left:55%;width:56px;height:80px;border:2px solid rgba(255,59,92,0.8);border-radius:4px;">
            <span style="position:absolute;top:-20px;left:0;font-size:10px;font-family:monospace;color:#ff3b5c;background:rgba(9,16,29,0.9);padding:1px 4px;border-radius:2px;">ID:7 INTRUSION</span></div>
            <div style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center;flex-direction:column;">
            <span style="font-size:28px;font-weight:800;color:#334155;letter-spacing:2px;">CAM-01</span><p style="color:#94a3b8;font-size:14px;margin:8px 0 0 0;">Processed Surveillance Video Stream</p>
            <p style="color:#64748b;font-size:12px;margin:4px 0 0 0;">Location: output/final_intrusion_video.mp4</p></div></div>""", unsafe_allow_html=True)

    with col_zone:
        st.markdown("""<div class="ibvap-card"><div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:14px;">
        <div style="display:flex;align-items:center;gap:10px;"><div style="width:34px;height:34px;border-radius:10px;background:rgba(255,59,92,0.15);border:1px solid rgba(255,59,92,0.3);display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:800;color:#ff3b5c;">ZN</div><h3 style="margin:0;">Restricted Zone</h3></div>
        <div style="display:flex;align-items:center;gap:6px;"><span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:#00f5d4;box-shadow:0 0 8px #00f5d4;"></span>
        <span style="font-size:12px;font-weight:700;color:#00f5d4;">ACTIVE</span></div></div>
        <div class="zone-viz"><div style="position:absolute;inset:0;opacity:0.25;background-image:linear-gradient(rgba(0,245,212,0.15) 1px,transparent 1px),linear-gradient(90deg,rgba(0,245,212,0.15) 1px,transparent 1px);background-size:24px 24px;"></div>
        <svg style="position:absolute;inset:0;width:100%;height:100%;" preserveAspectRatio="none" viewBox="0 0 200 160">
        <polygon points="60,40 140,40 150,120 50,120" fill="rgba(255,59,92,0.12)" stroke="rgba(255,59,92,0.7)" stroke-width="1.2" stroke-dasharray="4,3"/>
        <text x="100" y="85" fill="rgba(255,59,92,0.9)" font-size="8" text-anchor="middle" font-family="monospace" font-weight="bold">RESTRICTED ZONE</text>
        <circle cx="75" cy="70" r="3.5" fill="#00f5d4"/><text x="75" y="64" fill="#00f5d4" font-size="5" text-anchor="middle" font-family="monospace">T:2</text>
        <circle cx="110" cy="95" r="3.5" fill="#ff3b5c"/><text x="110" y="89" fill="#ff3b5c" font-size="5" text-anchor="middle" font-family="monospace">T:7</text>
        <circle cx="130" cy="110" r="3.5" fill="#ff3b5c"/><text x="130" y="104" fill="#ff3b5c" font-size="5" text-anchor="middle" font-family="monospace">T:36</text></svg></div>
        <div style="display:flex;gap:16px;margin-bottom:12px;"><div style="display:flex;align-items:center;gap:6px;"><span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:#00f5d4;"></span><span style="font-size:12px;color:#94a3b8;">Normal Track</span></div>
        <div style="display:flex;align-items:center;gap:6px;"><span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:#ff3b5c;"></span><span style="font-size:12px;color:#94a3b8;">Intrusion Event</span></div></div>
        <p style="font-size:12px;color:#94a3b8;line-height:1.5;margin:0;">The system automatically flags tracked targets entering the designated restricted border area. Person Track IDs are assigned by ByteTrack multi-object tracker.</p></div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)
    col_timeline, col_detail = st.columns([2, 1])

    with col_timeline:
        st.markdown(f"""<div class="ibvap-card"><div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:14px;">
        <h3 style="margin:0;">Intrusion Event Timeline</h3><span style="font-size:12px;color:#94a3b8;">{len(events)} events recorded</span></div>""", unsafe_allow_html=True)
        if not events:
            st.markdown('<p style="text-align:center;color:#94a3b8;padding:24px;">No intrusion events detected.</p>', unsafe_allow_html=True)
        else:
            for event in events:
                st.button(
                    f"{event.timestamp} — {event.event_type} — Track {event.person_track_id} — Frame {event.frame}",
                    key=f"timeline-{event.event_id}", use_container_width=True,
                    type="primary" if st.session_state.get("ibvap_selected_event") == event.event_id else "secondary",
                    on_click=set_selected_event, args=(event.event_id,)
                )
        st.markdown("</div>", unsafe_allow_html=True)

    with col_detail:
        selected_id = st.session_state.get("ibvap_selected_event")
        selected = next((e for e in events if e.event_id == selected_id), None)
        if selected:
            st.markdown(f"""<div class="ibvap-card"><h3>Selected Event Details</h3>
            <div style="display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid rgba(255,255,255,0.05);"><span style="font-size:13px;color:#94a3b8;">Event ID</span><span style="font-size:13px;font-family:monospace;font-weight:700;color:#00f5d4;">{selected.event_id}</span></div>
            <div style="display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid rgba(255,255,255,0.05);"><span style="font-size:13px;color:#94a3b8;">Track ID</span><span style="font-size:13px;font-weight:600;color:#f8fafc;">Track {selected.person_track_id}</span></div>
            <div style="display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid rgba(255,255,255,0.05);"><span style="font-size:13px;color:#94a3b8;">Timestamp</span><span style="font-size:13px;font-family:monospace;font-weight:600;color:#f8fafc;">{selected.timestamp}</span></div>
            <div style="display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid rgba(255,255,255,0.05);"><span style="font-size:13px;color:#94a3b8;">Frame</span><span style="font-size:13px;font-family:monospace;font-weight:600;color:#f8fafc;">{selected.frame}</span></div>
            <div style="display:flex;justify-content:space-between;padding:8px 0;"><span style="font-size:13px;color:#94a3b8;">Risk Level</span>{risk_badge(selected.risk)}</div></div>""", unsafe_allow_html=True)
            if selected.evidence_file:
                st.button("View Digital Evidence", key="surv-view-evidence", use_container_width=True, type="primary", on_click=set_evidence_view, args=(selected.event_id, "digital-evidence"))
        else:
            st.markdown("""<div class="ibvap-card"><p style="text-align:center;color:#94a3b8;padding:24px;">Select an event from the timeline to view full details.</p></div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# PAGE: SECURITY EVENTS
# ═══════════════════════════════════════════════════════════════════════════

def render_security_events(events):
    st.markdown(section_header("Security Events", f"Intrusion event management — {len(events)} event{'s' if len(events) != 1 else ''} recorded"), unsafe_allow_html=True)

    if not events:
        st.markdown(f'<div class="ibvap-card">{empty_state_html("EVT", "No intrusion events detected", "Surveillance system is operating normally. No security events have been recorded.")}</div>', unsafe_allow_html=True)
        return

    col_search, col_risk, col_status, col_sort = st.columns(4)
    with col_search:
        search = st.text_input("Search", placeholder="Event ID, track, timestamp...", key="evt-search")
    with col_risk:
        risk_filter = st.selectbox("Risk Filter", ["ALL", "HIGH", "MEDIUM", "LOW"], key="evt-risk-filter")
    with col_status:
        status_filter = st.selectbox("Status Filter", ["ALL", "Confirmed", "Pending", "Resolved"], key="evt-status-filter")
    with col_sort:
        sort_choice = st.selectbox("Sort Order", ["Frame (asc)", "Frame (desc)", "Timestamp (asc)", "Risk (desc)"], key="evt-sort")

    filtered = list(events)
    if search:
        q = search.lower()
        filtered = [e for e in filtered if q in e.event_id.lower() or q in e.event_type.lower() or q in str(e.person_track_id) or q in e.timestamp.lower() or q in e.risk.lower()]
    if risk_filter != "ALL":
        filtered = [e for e in filtered if e.risk == risk_filter]
    if status_filter != "ALL":
        filtered = [e for e in filtered if e.status == status_filter]

    risk_order = {"HIGH": 3, "MEDIUM": 2, "LOW": 1}
    if sort_choice == "Frame (asc)": filtered.sort(key=lambda e: e.frame)
    elif sort_choice == "Frame (desc)": filtered.sort(key=lambda e: e.frame, reverse=True)
    elif sort_choice == "Timestamp (asc)": filtered.sort(key=lambda e: e.timestamp)
    elif sort_choice == "Risk (desc)": filtered.sort(key=lambda e: risk_order.get(e.risk, 0), reverse=True)

    if not filtered:
        st.markdown('<div class="ibvap-card"><p style="text-align:center;color:#94a3b8;padding:24px;">No events match the selected filters.</p></div>', unsafe_allow_html=True)
    else:
        rows_html = ""
        for event in filtered:
            ev_label = '<span style="color:#00f5d4;font-weight:600;">Available</span>' if event.evidence_file else '<span style="color:#64748b;">N/A</span>'
            rows_html += f"""<tr><td style="font-family:monospace;font-weight:700;color:#00f5d4;">{event.event_id}</td>
            <td style="font-weight:600;">{event.event_type}</td><td>Track {event.person_track_id}</td>
            <td style="font-family:monospace;">{event.frame}</td><td style="font-family:monospace;">{event.timestamp}</td>
            <td>{risk_badge(event.risk)}</td><td>{ev_label}</td>
            <td><span style="color:#10b981;font-weight:600;">{event.status}</span></td></tr>"""

        st.markdown(f"""<div class="ibvap-card" style="padding:0;overflow:hidden;"><table class="data-table"><thead><tr>
        <th>Event ID</th><th>Event Type</th><th>Track ID</th><th>Frame</th><th>Timestamp</th><th>Risk</th><th>Evidence</th><th>Status</th>
        </tr></thead><tbody>{rows_html}</tbody></table></div>""", unsafe_allow_html=True)

        st.markdown("<div style='height:18px;'></div>", unsafe_allow_html=True)
        st.markdown("#### Inspect Event Details")

        cols = st.columns(min(len(filtered), 3))
        for i, event in enumerate(filtered):
            with cols[i % 3]:
                st.button(f"View {event.event_id}", key=f"evt-detail-{event.event_id}", use_container_width=True, on_click=set_selected_event, args=(event.event_id,))

    selected_id = st.session_state.get("ibvap_selected_event")
    selected = next((e for e in events if e.event_id == selected_id), None)
    if selected:
        _render_event_modal(selected)


def _render_event_modal(event):
    ev_color = "#00f5d4" if event.evidence_file else "#94a3b8"
    ev_text = "Available" if event.evidence_file else "N/A"
    st.markdown(f"""
    <div class="ibvap-card" style="border: 2px solid rgba(0,245,212,0.4); box-shadow: 0 0 30px rgba(0,245,212,0.15);">
    <div style="display:flex;align-items:center;gap:14px;margin-bottom:18px;">
    <div style="width:44px;height:44px;border-radius:12px;background:rgba(255,59,92,0.15);border:1px solid rgba(255,59,92,0.3);display:flex;align-items:center;justify-content:center;font-size:14px;font-weight:800;color:#ff3b5c;letter-spacing:0.5px;">SEC</div>
    <div><h3 style="margin:0;font-size:18px;font-weight:800;color:#ffffff;">Security Event Summary</h3><p style="margin:2px 0 0 0;font-size:13px;font-family:monospace;color:#00f5d4;">{event.event_id}</p></div></div>
    <div style="display:flex;align-items:center;justify-content:space-between;padding:12px 16px;background:rgba(0,0,0,0.2);border:1px solid rgba(255,255,255,0.08);border-radius:10px;margin-bottom:16px;">
    <span style="font-size:13px;color:#94a3b8;font-weight:600;">Risk Classification</span>{risk_badge(event.risk)}</div>
    <div style="display:flex;justify-content:space-between;padding:10px 14px;background:rgba(255,255,255,0.03);border-radius:8px;margin-bottom:6px;"><span style="font-size:13px;color:#94a3b8;">Event ID</span><span style="font-size:13px;font-family:monospace;font-weight:700;color:#00f5d4;">{event.event_id}</span></div>
    <div style="display:flex;justify-content:space-between;padding:10px 14px;background:rgba(255,255,255,0.03);border-radius:8px;margin-bottom:6px;"><span style="font-size:13px;color:#94a3b8;">Event Type</span><span style="font-size:13px;font-weight:600;color:#f8fafc;">{event.event_type}</span></div>
    <div style="display:flex;justify-content:space-between;padding:10px 14px;background:rgba(255,255,255,0.03);border-radius:8px;margin-bottom:6px;"><span style="font-size:13px;color:#94a3b8;">Person Track</span><span style="font-size:13px;font-weight:600;color:#f8fafc;">Track {event.person_track_id}</span></div>
    <div style="display:flex;justify-content:space-between;padding:10px 14px;background:rgba(255,255,255,0.03);border-radius:8px;margin-bottom:6px;"><span style="font-size:13px;color:#94a3b8;">Frame</span><span style="font-size:13px;font-family:monospace;font-weight:600;color:#f8fafc;">{event.frame}</span></div>
    <div style="display:flex;justify-content:space-between;padding:10px 14px;background:rgba(255,255,255,0.03);border-radius:8px;margin-bottom:6px;"><span style="font-size:13px;color:#94a3b8;">Timestamp</span><span style="font-size:13px;font-family:monospace;font-weight:600;color:#f8fafc;">{event.timestamp}</span></div>
    <div style="display:flex;justify-content:space-between;padding:10px 14px;background:rgba(255,255,255,0.03);border-radius:8px;margin-bottom:6px;"><span style="font-size:13px;color:#94a3b8;">Detection Method</span><span style="font-size:13px;font-weight:600;color:#f8fafc;">{event.detection_method}</span></div>
    <div style="display:flex;justify-content:space-between;padding:10px 14px;background:rgba(255,255,255,0.03);border-radius:8px;margin-bottom:18px;"><span style="font-size:13px;color:#94a3b8;">Evidence Reference</span><span style="font-size:13px;font-weight:700;color:{ev_color};">{ev_text}</span></div>
    </div>""", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        if event.evidence_file:
            st.button("View Evidence", key=f"modal-evidence-{event.event_id}", use_container_width=True, type="primary", on_click=set_evidence_view, args=(event.event_id, "digital-evidence"))
    with col2:
        st.button("Open Video Stream", key=f"modal-video-{event.event_id}", use_container_width=True, on_click=set_page, args=("surveillance",))
    with col3:
        st.download_button("Download JSON", data=json.dumps(event.to_dict(), indent=2), file_name=f"{event.event_id}_event.json", mime="application/json", key=f"modal-dl-{event.event_id}", use_container_width=True)
    st.button("Close Modal", key="modal-close", use_container_width=True, on_click=set_selected_event, args=(None,))


# ═══════════════════════════════════════════════════════════════════════════
# PAGE: DIGITAL EVIDENCE
# ═══════════════════════════════════════════════════════════════════════════

def render_digital_evidence(events):
    with_evidence = [e for e in events if e.evidence_file]
    st.markdown(section_header("Digital Evidence", f"Visual evidence captured for intrusion events — {len(with_evidence)} item{'s' if len(with_evidence) != 1 else ''}"), unsafe_allow_html=True)

    if not with_evidence:
        st.markdown(f'<div class="ibvap-card">{empty_state_html("EVD", "No Digital Evidence Available", "No evidence images have been captured. Evidence is generated when intrusion events are detected.")}</div>', unsafe_allow_html=True)
        return

    for i, event in enumerate(with_evidence):
        evidence_id = f"EV-{i+1:03d}"
        col_img, col_info = st.columns([3, 2])

        with col_img:
            try:
                img_bytes = fetch_image_bytes(event.evidence_file) if event.evidence_file else None
                if img_bytes:
                    st.image(img_bytes, caption=f"{evidence_id} — {event.event_id}", use_container_width=True)
                else:
                    st.markdown('<div style="background:#09101d;aspect-ratio:16/9;border-radius:14px;display:flex;align-items:center;justify-content:center;border:1px solid rgba(255,255,255,0.08);"><span style="font-size:22px;font-weight:800;color:#64748b;letter-spacing:1px;">EVD SNAPSHOT</span></div>', unsafe_allow_html=True)
            except Exception:
                st.markdown('<div style="background:#09101d;aspect-ratio:16/9;border-radius:14px;display:flex;align-items:center;justify-content:center;border:1px solid rgba(255,255,255,0.08);"><span style="font-size:22px;font-weight:800;color:#64748b;letter-spacing:1px;">EVD SNAPSHOT</span></div>', unsafe_allow_html=True)

        with col_info:
            st.markdown(f"""<div class="ibvap-card"><div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px;">
            <span style="font-size:16px;font-weight:800;color:#00f5d4;font-family:monospace;">{evidence_id}</span>{risk_badge(event.risk)}</div>
            <div style="display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid rgba(255,255,255,0.05);"><span style="font-size:13px;color:#94a3b8;">Event ID</span><span style="font-size:13px;font-family:monospace;color:#f8fafc;font-weight:700;">{event.event_id}</span></div>
            <div style="display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid rgba(255,255,255,0.05);"><span style="font-size:13px;color:#94a3b8;">Event Type</span><span style="font-size:13px;color:#f8fafc;font-weight:600;">{event.event_type}</span></div>
            <div style="display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid rgba(255,255,255,0.05);"><span style="font-size:13px;color:#94a3b8;">Person Track</span><span style="font-size:13px;color:#f8fafc;font-weight:600;">Track {event.person_track_id}</span></div>
            <div style="display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid rgba(255,255,255,0.05);"><span style="font-size:13px;color:#94a3b8;">Frame</span><span style="font-size:13px;font-family:monospace;color:#f8fafc;font-weight:600;">{event.frame}</span></div>
            <div style="display:flex;justify-content:space-between;padding:8px 0;"><span style="font-size:13px;color:#94a3b8;">Timestamp</span><span style="font-size:13px;font-family:monospace;color:#f8fafc;font-weight:600;">{event.timestamp}</span></div></div>""", unsafe_allow_html=True)

            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.button("Zoom", key=f"zoom-{event.event_id}", use_container_width=True, on_click=set_evidence_view, args=(event.event_id,))
            with col_b:
                st.markdown(f'<a href="{event.evidence_file}" target="_blank" download style="display:inline-block;width:100%;text-align:center;padding:8px;background:rgba(255,255,255,0.06);border-radius:10px;color:#00f5d4;text-decoration:none;font-weight:600;">Download</a>', unsafe_allow_html=True)
            with col_c:
                st.button("Event", key=f"evt-link-{event.event_id}", use_container_width=True, on_click=set_evidence_view, args=(event.event_id, "security-events"))

        st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)

    view_id = st.session_state.get("ibvap_evidence_view")
    if view_id:
        view_event = next((e for e in events if e.event_id == view_id), None)
        if view_event and view_event.evidence_file:
            st.markdown("---")
            st.markdown(f"#### High Resolution Evidence Viewer — {view_event.event_id}")
            try:
                high_res_bytes = fetch_image_bytes(view_event.evidence_file)
                st.image(high_res_bytes, use_container_width=True)
            except Exception:
                st.image(view_event.evidence_file, use_container_width=True)
            st.button("Close Viewer", key="close-evidence-view", on_click=set_evidence_view, args=(None,))


# ═══════════════════════════════════════════════════════════════════════════
# PAGE: AUDIT LOG
# ═══════════════════════════════════════════════════════════════════════════

def render_audit_log(events):
    st.markdown(section_header("Audit Log", f"Structured security audit trail & tamper verification — {len(events)} record{'s' if len(events) != 1 else ''}"), unsafe_allow_html=True)

    st.markdown("""<div class="ibvap-card" style="display:flex;align-items:flex-start;gap:14px;">
    <div style="width:40px;height:40px;border-radius:10px;background:rgba(0,245,212,0.15);border:1px solid rgba(0,245,212,0.3);display:flex;align-items:center;justify-content:center;flex-shrink:0;font-size:12px;font-weight:800;color:#00f5d4;">LOG</div>
    <p style="font-size:13px;color:#94a3b8;line-height:1.6;margin:0;">Each intrusion event is cryptographically timestamped and recorded with track ID, frame reference, risk classification and visual evidence references. Export structured CSV audit logs for compliance.</p></div>""", unsafe_allow_html=True)

    if not events:
        st.markdown(f'<div class="ibvap-card">{empty_state_html("LOG", "Audit Log Unavailable", "No audit records found. Expected output file: output/intrusion_log.csv")}</div>', unsafe_allow_html=True)
        return

    col_search, col_download = st.columns([3, 1])
    with col_search:
        search = st.text_input("Search audit records...", key="audit-search")
    with col_download:
        st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)
        st.download_button("Export Audit Log CSV", data=events_to_csv(events), file_name="ibvap_security_audit_log.csv", mime="text/csv", use_container_width=True, type="primary")

    filtered = list(events)
    if search:
        q = search.lower()
        filtered = [e for e in events if q in e.event_id.lower() or q in e.event_type.lower() or q in str(e.person_track_id) or q in e.timestamp.lower() or q in e.risk.lower()]

    if not filtered:
        st.markdown('<div class="ibvap-card"><p style="text-align:center;color:#94a3b8;padding:24px;">No records match your search.</p></div>', unsafe_allow_html=True)
    else:
        rows_html = ""
        for event in filtered:
            created = event.created_at[:19].replace("T", " ") if event.created_at else "N/A"
            evidence = "Available" if event.evidence_file else "N/A"
            rows_html += f"""<tr><td style="font-family:monospace;font-weight:700;color:#00f5d4;">{event.event_id}</td>
            <td>{event.event_type}</td><td>Track {event.person_track_id}</td><td style="font-family:monospace;">{event.frame}</td>
            <td style="font-family:monospace;">{event.timestamp}</td><td>{risk_badge(event.risk)}</td><td>{evidence}</td>
            <td><span style="color:#10b981;font-weight:600;">{event.status}</span></td>
            <td style="font-family:monospace;font-size:12px;color:#94a3b8;">{created}</td></tr>"""

        st.markdown(f"""<div class="ibvap-card" style="padding:0;overflow:hidden;"><table class="data-table"><thead><tr>
        <th>Event ID</th><th>Event Type</th><th>Track ID</th><th>Frame</th><th>Timestamp</th><th>Risk</th><th>Evidence Ref</th><th>Status</th><th>Created At</th>
        </tr></thead><tbody>{rows_html}</tbody></table></div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:24px;'></div>", unsafe_allow_html=True)
    st.markdown("#### Audit Integrity Verification")

    verified, message, verified_count = verify_secure_audit_log()

    if verified:
        st.success("✓ Audit Log Integrity VERIFIED (SHA-256 Chain Intact)")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Hash Algorithm", "SHA-256")
        with col2:
            st.metric("Records Verified", verified_count)
        with col3:
            st.metric("Chain Integrity", "VALID")

        if os.path.exists(ROOT_HASH_PATH):
            with open(ROOT_HASH_PATH, "r") as f:
                root_hash = f.read().strip()
            short_hash = root_hash[:16] + "..." + root_hash[-8:]
            st.markdown(f"**Root Hash:** `{short_hash}`")
    else:
        st.error(f"⚠ Audit Integrity Warning: {message}")

    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
    st.markdown("#### Blockchain Audit Ledger Status")

    blockchain_valid, blockchain_message, block_count = verify_blockchain_ledger()
    if blockchain_valid:
        st.success("✓ Blockchain Audit Ledger VERIFIED")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Ledger Architecture", "SHA-256 Block Chain")
        with col2:
            st.metric("Total Blocks", block_count)
        with col3:
            st.metric("Ledger Integrity", "VALID")
        st.caption("Each block contains the event record, previous block hash, and current block signature.")
    else:
        st.warning(f"⚠ Blockchain Ledger Status: {blockchain_message}")

    st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)
    st.markdown("#### Cybersecurity Architecture")
    col_current, col_future = st.columns(2)

    with col_current:
        items = ["AI-generated intrusion events", "Cryptographic timestamping", "Risk classification engine", "Visual evidence capture", "SHA-256 CSV audit log"]
        items_html = "".join([f'<div style="display:flex;align-items:center;gap:10px;padding:8px 0;font-size:13px;color:#94a3b8;"><span style="color:#00f5d4;font-size:16px;">&bull;</span> {item}</div>' for item in items])
        st.markdown(f"""<div class="ibvap-card"><div style="display:flex;align-items:center;gap:10px;margin-bottom:14px;">
        <div style="width:36px;height:36px;border-radius:10px;background:rgba(16,185,129,0.15);border:1px solid rgba(16,185,129,0.3);display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:800;color:#10b981;">SEC</div>
        <div><h3 style="margin:0;">Deployed Security Architecture</h3><span style="font-size:10px;font-weight:700;color:#10b981;letter-spacing:0.5px;">ACTIVE</span></div></div>{items_html}</div>""", unsafe_allow_html=True)

    with col_future:
        steps = ["Event Record", "Cryptographic Hash", "Permissioned Blockchain", "Tamper-Evident Ledger"]
        steps_html = "".join([f'<div style="display:flex;align-items:center;gap:10px;padding:8px 0;font-size:13px;color:#94a3b8;"><span style="width:22px;height:22px;border-radius:6px;background:rgba(255,255,255,0.06);display:flex;align-items:center;justify-content:center;font-size:11px;font-family:monospace;color:#00f5d4;">{i+1}</span> {s}</div>' for i, s in enumerate(steps)])
        st.markdown(f"""<div class="ibvap-card" style="border:2px dashed rgba(255,255,255,0.15);"><div style="display:flex;align-items:center;gap:10px;margin-bottom:14px;">
        <div style="width:36px;height:36px;border-radius:10px;background:rgba(245,158,11,0.15);border:1px solid rgba(245,158,11,0.3);display:flex;align-items:center;justify-content:center;font-size:10px;font-weight:800;color:#f59e0b;">NEXT</div>
        <div><h3 style="margin:0;">Future Enterprise Blockchain</h3><span style="font-size:10px;font-weight:700;color:#f59e0b;letter-spacing:0.5px;">ROADMAP</span></div></div>
        {steps_html}<p style="font-size:12px;color:#64748b;margin-top:14px;padding-top:12px;border-top:1px solid rgba(255,255,255,0.06);">Multi-node permissioned blockchain integration for enterprise auditing.</p></div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# PAGE: SYSTEM
# ═══════════════════════════════════════════════════════════════════════════

def render_system(events):
    st.markdown(section_header("System", "Technical system architecture & environment information"), unsafe_allow_html=True)

    st.markdown("""<div class="ibvap-card"><div style="display:flex;align-items:center;gap:16px;">
    <div style="width:48px;height:48px;border-radius:14px;background:linear-gradient(135deg,#00f5d4,#38bdf8);display:flex;align-items:center;justify-content:center;font-size:16px;font-weight:800;color:#070c18;box-shadow:0 0 20px rgba(0,245,212,0.4);">IB</div>
    <div><h3 style="margin:0;font-size:18px;font-weight:800;color:#ffffff;">IBVAP Engine</h3><p style="margin:2px 0 0 0;font-size:13px;color:#94a3b8;">Intelligent Border Video Analytics Platform — SIH 2026</p></div>
    <div style="margin-left:auto;display:flex;align-items:center;gap:6px;padding:8px 16px;border-radius:20px;background:rgba(16,185,129,0.15);border:1px solid rgba(16,185,129,0.3);">
    <span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:#10b981;box-shadow:0 0 8px #10b981;"></span><span style="font-size:12px;font-weight:700;color:#10b981;letter-spacing:0.5px;">OPERATIONAL</span></div></div></div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
    modules = [
        ("AI", "AI Detection", "YOLO11", "Person detection neural model"),
        ("TRK", "Object Tracking", "ByteTrack", "Multi-object tracker"),
        ("VID", "Video Processing", "OpenCV", "Frame processing pipeline"),
        ("ZN", "Restricted Zone", "Polygon Zone", "Perimeter violation check"),
        ("RISK", "Risk Engine", "HIGH Alert", "Risk classification rules"),
        ("LOG", "Security Logging", "CSV Audit Trail", "Event persistence"),
        ("WEB", "Frontend Platform", "Streamlit + Python", "Web command dashboard"),
    ]
    cols = st.columns(3)
    for i, (icon, label, value, desc) in enumerate(modules):
        with cols[i % 3]:
            st.markdown(f"""<div class="ibvap-card" style="padding:18px;"><div style="display:flex;align-items:center;gap:12px;margin-bottom:10px;">
            <div style="width:38px;height:38px;border-radius:10px;background:rgba(0,245,212,0.12);border:1px solid rgba(0,245,212,0.25);display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:800;color:#00f5d4;">{icon}</div>
            <span style="font-size:13px;font-weight:600;color:#94a3b8;">{label}</span></div>
            <p style="font-size:16px;font-weight:800;color:#ffffff;margin:0;">{value}</p><p style="font-size:11px;color:#64748b;margin:4px 0 0 0;">{desc}</p></div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
    st.markdown(f'<div class="pipeline-container">{security_pipeline_html()}</div>', unsafe_allow_html=True)

    st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)
    st.markdown("#### Platform Technical Overview")
    col_current, col_future = st.columns(2)

    with col_current:
        steps = ["Surveillance Video Feed", "YOLO11 Object Detection", "ByteTrack Target Association", "Restricted Polygon Zone Check", "Audit Event Logging"]
        steps_html = "".join([f'<div style="display:flex;align-items:center;gap:10px;padding:8px 0;font-size:13px;color:#94a3b8;"><span style="color:#00f5d4;font-size:16px;">&bull;</span> {s}</div>' for s in steps])
        st.markdown(f"""<div class="ibvap-card"><div style="display:flex;align-items:center;gap:10px;margin-bottom:14px;"><span style="font-size:11px;font-weight:800;color:#00f5d4;">CORE</span><h3 style="margin:0;">Current Core Pipeline</h3></div>{steps_html}</div>""", unsafe_allow_html=True)

    with col_future:
        steps = ["Structured Event Generation", "SHA-256 Record Hash", "Permissioned Blockchain", "Immutable Verification"]
        steps_html = "".join([f'<div style="display:flex;align-items:center;gap:10px;padding:8px 0;font-size:13px;color:#94a3b8;"><span style="display:inline-block;width:14px;height:14px;border-radius:50%;border:1px solid #00f5d4;"></span> {s}</div>' for s in steps])
        st.markdown(f"""<div class="ibvap-card" style="border:2px dashed rgba(255,255,255,0.15);"><div style="display:flex;align-items:center;gap:10px;margin-bottom:14px;"><span style="font-size:11px;font-weight:800;color:#f59e0b;">PLAN</span><div><h3 style="margin:0;">Future Enterprise Scale</h3><span style="font-size:10px;font-weight:700;color:#f59e0b;letter-spacing:0.5px;">PLANNED</span></div></div>
        {steps_html}<p style="font-size:12px;color:#64748b;margin-top:14px;padding-top:12px;border-top:1px solid rgba(255,255,255,0.06);">Multi-camera distributed stream ingestion roadmap.</p></div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# MAIN APPLICATION & NAVIGATION
# ═══════════════════════════════════════════════════════════════════════════

st.set_page_config(page_title="IBVAP — Intelligent Border Video Analytics Platform", layout="wide", initial_sidebar_state="expanded")

def inject_custom_css():
    theme = st.session_state.get("ibvap_theme", "dark")
    sidebar_open = st.session_state.get("ibvap_sidebar_open", True)

    if theme == "dark":
        bg_main = "#060b14"
        bg_card = "#0e1726"
        bg_sidebar = "#09101d"
        text_primary = "#f8fafc"
        text_secondary = "#94a3b8"
        border_color = "rgba(255, 255, 255, 0.08)"
        header_bg = "linear-gradient(135deg, #091222 0%, #132238 50%, #091222 100%)"
        header_border = "1px solid rgba(0, 245, 212, 0.2)"
        table_th_bg = "#131f37"
        table_td_border = "rgba(255, 255, 255, 0.05)"
        table_hover = "#192843"
    else:
        bg_main = "#f1f5f9"
        bg_card = "#ffffff"
        bg_sidebar = "#0f172a"
        text_primary = "#0f172a"
        text_secondary = "#475569"
        border_color = "#e2e8f0"
        header_bg = "linear-gradient(135deg, #0f172a 0%, #1e293b 100%)"
        header_border = "1px solid #cbd5e1"
        table_th_bg = "#f8fafc"
        table_td_border = "#f1f5f9"
        table_hover = "#f8fafc"

    sidebar_css = "" if sidebar_open else """
    [data-testid="stSidebar"] { display: none !important; }
    .main .block-container { max-width: 100% !important; padding-left: 2.5rem !important; padding-right: 2.5rem !important; }
    """

    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    @keyframes pulseDot {{
        0% {{ box-shadow: 0 0 0 0 rgba(0, 245, 212, 0.6); }}
        70% {{ box-shadow: 0 0 0 10px rgba(0, 245, 212, 0); }}
        100% {{ box-shadow: 0 0 0 0 rgba(0, 245, 212, 0); }}
    }}

    html, body, [data-testid="stAppViewContainer"] {{
        font-family: 'Plus Jakarta Sans', sans-serif;
        background-color: {bg_main} !important;
        color: {text_primary} !important;
        -webkit-font-smoothing: antialiased;
    }}
    .main .block-container {{ max-width: 1440px; padding-top: 1rem; padding-bottom: 2.5rem; }}
    #MainMenu, footer, header, .stDeployButton {{ visibility: hidden; display: none; }}

    {sidebar_css}

    [data-testid="stSidebar"] {{
        background-color: {bg_sidebar} !important;
        border-right: 1px solid {border_color};
    }}

    .ibvap-header {{
        background: {header_bg};
        border: {header_border};
        border-radius: 18px;
        padding: 20px 26px;
        margin-bottom: 20px;
        box-shadow: 0 12px 36px rgba(0,0,0,0.25);
    }}
    .ibvap-header h1 {{
        color: #ffffff;
        font-size: 24px;
        font-weight: 800;
        margin: 0;
        letter-spacing: -0.5px;
    }}
    .ibvap-header p {{
        color: #94a3b8;
        font-size: 13px;
        margin: 3px 0 0 0;
    }}
    .ibvap-status-badge {{
        background: rgba(0, 245, 212, 0.12);
        border: 1px solid rgba(0, 245, 212, 0.3);
        border-radius: 20px;
        padding: 6px 14px;
        font-size: 11px;
        font-weight: 700;
        color: #00f5d4;
        display: inline-flex;
        align-items: center;
        gap: 6px;
        letter-spacing: 0.5px;
    }}
    .ibvap-clock {{
        color: #94a3b8;
        font-size: 12px;
        font-family: monospace;
        font-weight: 600;
    }}
    .ibvap-card {{
        background: {bg_card};
        border: 1px solid {border_color};
        border-radius: 16px;
        padding: 22px;
        margin-bottom: 16px;
        box-shadow: 0 6px 24px rgba(0, 0, 0, 0.12);
        color: {text_primary};
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }}
    .ibvap-card h3 {{
        font-size: 16px;
        font-weight: 700;
        color: {text_primary};
        margin: 0 0 12px 0;
    }}
    .ibvap-card-threat {{
        background: rgba(255, 59, 92, 0.08) !important;
        border: 1px solid rgba(255, 59, 92, 0.3) !important;
    }}
    .ibvap-card-secure {{
        background: rgba(16, 185, 129, 0.08) !important;
        border: 1px solid rgba(16, 185, 129, 0.3) !important;
    }}
    .health-grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; }}
    .health-item {{
        display: flex; align-items: center; gap: 12px; padding: 12px 14px;
        background: {bg_card}; border: 1px solid {border_color}; border-radius: 12px;
    }}
    .health-item-icon {{
        width: 38px; height: 38px; border-radius: 10px;
        background: rgba(0, 245, 212, 0.1); border: 1px solid rgba(0, 245, 212, 0.2);
        display: flex; align-items: center; justify-content: center;
        font-size: 11px; font-weight: 800; color: #00f5d4; flex-shrink: 0;
    }}
    .health-item-label {{ font-size: 13px; font-weight: 700; color: {text_primary}; }}
    .health-item-sub {{ font-size: 11px; color: {text_secondary}; }}

    .event-item {{
        display: flex; align-items: center; justify-content: space-between;
        padding: 14px 18px; background: {bg_card}; border: 1px solid {border_color};
        border-radius: 12px; margin-bottom: 8px; transition: all 0.2s ease;
    }}
    .event-item:hover {{
        background: {table_hover}; border-color: rgba(0,245,212,0.3);
    }}

    .ibvap-sidebar-header {{
        padding: 14px 4px 20px; border-bottom: 1px solid {border_color}; margin-bottom: 14px;
    }}
    .ibvap-sidebar-header h1 {{ color: #ffffff; font-size: 20px; font-weight: 800; margin: 0; display: flex; align-items: center; gap: 10px; }}
    .ibvap-sidebar-header p {{ color: #00f5d4; font-size: 11px; text-transform: uppercase; letter-spacing: 1px; font-weight: 700; margin: 4px 0 0 0; }}
    .ibvap-sidebar-section-label {{ color: #64748b; font-size: 11px; text-transform: uppercase; letter-spacing: 1px; font-weight: 800; margin: 20px 0 10px 0; }}
    .ibvap-sidebar-status-item {{ display: flex; align-items: center; gap: 10px; padding: 7px 0; color: #cbd5e1; font-size: 12px; font-weight: 600; }}
    .ibvap-sidebar-tech {{ display: flex; gap: 8px; padding: 16px 0 4px; border-top: 1px solid {border_color}; margin-top: 22px; flex-wrap: wrap; }}
    .ibvap-sidebar-tech span {{ color: #94a3b8; font-size: 11px; font-weight: 700; background: rgba(255,255,255,0.06); padding: 4px 10px; border-radius: 6px; border: 1px solid rgba(255,255,255,0.08); }}

    [data-testid="stSidebar"] .stButton > button {{
        width: 100%; text-align: left; justify-content: flex-start;
        background: transparent; border: 1px solid transparent; color: #94a3b8;
        font-weight: 600; font-size: 13px; border-radius: 12px; padding: 11px 16px;
        transition: all 0.2s ease;
    }}
    [data-testid="stSidebar"] .stButton > button:hover {{
        background: rgba(255,255,255,0.06); color: #ffffff; border-color: rgba(255,255,255,0.1);
    }}
    [data-testid="stSidebar"] .stButton > button[kind="primary"] {{
        background: linear-gradient(135deg, rgba(0,245,212,0.2) 0%, rgba(56,189,248,0.15) 100%) !important;
        color: #00f5d4 !important; border: 1px solid rgba(0,245,212,0.4) !important;
        font-weight: 800 !important; box-shadow: 0 4px 14px rgba(0,245,212,0.15);
    }}

    .data-table {{ width: 100%; border-collapse: collapse; border-radius: 12px; overflow: hidden; }}
    .data-table th {{ background: {table_th_bg}; border-bottom: 1px solid {border_color}; padding: 14px 18px; text-align: left; font-size: 12px; font-weight: 800; color: {text_secondary}; text-transform: uppercase; letter-spacing: 0.6px; }}
    .data-table td {{ padding: 14px 18px; border-bottom: 1px solid {table_td_border}; font-size: 13px; color: {text_primary}; }}
    .data-table tr:hover td {{ background: {table_hover}; }}

    .ibvap-footer {{
        border-top: 1px solid {border_color}; padding: 22px 0; margin-top: 40px;
        display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px;
    }}
    .ibvap-footer-text {{ font-size: 12px; color: {text_secondary}; }}
    .ibvap-footer-tech {{ font-size: 11px; color: {text_secondary}; font-weight: 600; }}

    .stButton > button {{
        border-radius: 10px; font-weight: 600; font-size: 13px; transition: all 0.2s ease;
    }}
    </style>
    """, unsafe_allow_html=True)


if "ibvap_page" not in st.session_state:
    st.session_state.ibvap_page = "command-center"
if "ibvap_selected_event" not in st.session_state:
    st.session_state.ibvap_selected_event = None
if "ibvap_evidence_view" not in st.session_state:
    st.session_state.ibvap_evidence_view = None
if "ibvap_theme" not in st.session_state:
    st.session_state.ibvap_theme = "dark"
if "ibvap_sidebar_open" not in st.session_state:
    st.session_state.ibvap_sidebar_open = True

PAGES = [
    ("command-center", "Command Center"),
    ("surveillance", "Surveillance"),
    ("security-events", "Security Events"),
    ("digital-evidence", "Digital Evidence"),
    ("audit-log", "Audit Log"),
    ("system", "System"),
]


def set_page(page_id):
    st.session_state.ibvap_page = page_id

def set_selected_event(event_id):
    st.session_state.ibvap_selected_event = event_id

def set_evidence_view(event_id, page_id=None):
    st.session_state.ibvap_evidence_view = event_id
    if page_id:
        st.session_state.ibvap_page = page_id

def toggle_sidebar():
    st.session_state.ibvap_sidebar_open = not st.session_state.get("ibvap_sidebar_open", True)

def toggle_theme():
    st.session_state.ibvap_theme = "light" if st.session_state.get("ibvap_theme") == "dark" else "dark"


def render_sidebar():
    current = st.session_state.ibvap_page
    sidebar_open = st.session_state.get("ibvap_sidebar_open", True)

    with st.sidebar:
        # Top toggle button inside sidebar header
        col_t1, col_t2 = st.columns([3, 1])
        with col_t1:
            st.markdown(f"""
            <div style="padding-top:4px;">
                <h1 style="color:#ffffff;font-size:20px;font-weight:800;margin:0;display:flex;align-items:center;gap:8px;">
                    {get_icon_svg("shield", color="#00f5d4", size=22)} IBVAP
                </h1>
            </div>
            """, unsafe_allow_html=True)
        with col_t2:
            st.button(":material/left_panel_close:", key="sidebar_close_toggle", help="Collapse Sidebar", on_click=toggle_sidebar)

        st.markdown("""
        <div style="margin-bottom:16px;">
            <p style="color:#00f5d4;font-size:10px;text-transform:uppercase;letter-spacing:1px;font-weight:800;margin:2px 0 0 0;">Border Video Analytics</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<p class="ibvap-sidebar-section-label">Navigation</p>', unsafe_allow_html=True)
        page_icons = {
            "command-center": ":material/dashboard:",
            "surveillance": ":material/videocam:",
            "security-events": ":material/warning:",
            "digital-evidence": ":material/photo_camera:",
            "audit-log": ":material/verified_user:",
            "system": ":material/settings:",
        }
        for pid, label in PAGES:
            btn_label = f"{page_icons.get(pid, ':material/chevron_right:')} {label}"
            st.button(
                btn_label, key=f"sidebar-nav-{pid}", use_container_width=True,
                type="primary" if current == pid else "secondary",
                on_click=set_page, args=(pid,)
            )

        st.markdown('<p class="ibvap-sidebar-section-label">System Modules</p>', unsafe_allow_html=True)
        status_items = "".join([f'<div class="ibvap-sidebar-status-item">{status_indicator(True)}<span>{label}</span></div>' for label in ["AI Detection Engine", "ByteTrack Tracker", "Zone Monitoring", "Audit Security Logger"]])
        st.markdown(status_items, unsafe_allow_html=True)

        st.markdown('<div class="ibvap-sidebar-tech"><span>YOLO11</span><span>ByteTrack</span><span>OpenCV</span><span>MongoDB</span></div>', unsafe_allow_html=True)


def render_header():
    now = datetime.now().strftime("%H:%M:%S")
    theme = st.session_state.get("ibvap_theme", "dark")
    sidebar_open = st.session_state.get("ibvap_sidebar_open", True)

    col_left, col_right = st.columns([3.2, 2.2])

    with col_left:
        c_toggle, c_title = st.columns([0.4, 3])
        with c_toggle:
            toggle_icon = ":material/left_panel_close:" if sidebar_open else ":material/left_panel_open:"
            toggle_help = "Collapse Sidebar Menu" if sidebar_open else "Expand Sidebar Menu"
            st.button(toggle_icon, key="top_sidebar_toggle", help=toggle_help, use_container_width=True, on_click=toggle_sidebar)

        with c_title:
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:14px;">
                <div style="width:44px;height:44px;border-radius:12px;background:linear-gradient(135deg, #00f5d4 0%, #38bdf8 100%);
                display:flex;align-items:center;justify-content:center;box-shadow:0 0 20px rgba(0,245,212,0.4);flex-shrink:0;">
                    {get_icon_svg("shield", color="#070c18", size=26)}
                </div>
                <div>
                    <h1 style="color:#ffffff;font-size:22px;font-weight:800;margin:0;letter-spacing:-0.5px;">IBVAP</h1>
                    <p style="color:#94a3b8;font-size:12px;margin:2px 0 0 0;font-weight:600;">Intelligent Border Video Analytics Platform</p>
                </div>
            </div>
            """, unsafe_allow_html=True)

    with col_right:
        c1, c2 = st.columns([1.2, 1.8])
        with c1:
            theme_icon = ":material/light_mode:" if theme == "dark" else ":material/dark_mode:"
            theme_help = "Switch to Light Theme" if theme == "dark" else "Switch to Dark Theme"
            st.button(theme_icon, key="top_theme_toggle", help=theme_help, use_container_width=True, on_click=toggle_theme)
        with c2:
            st.markdown(f"""
            <div style="text-align:right;padding-top:2px;">
                <span class="ibvap-status-badge">{status_indicator(True)} OPERATIONAL</span>
                <div class="ibvap-clock" style="margin-top:4px;">{now}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)


def render_footer():
    st.markdown(f"""<div class="ibvap-footer">
    <span class="ibvap-footer-text"><strong>IBVAP</strong> — Intelligent Border Video Analytics Platform</span>
    <span class="ibvap-footer-tech">YOLO11 • ByteTrack • OpenCV • SIH 2026 — Blockchain & Cybersecurity</span>
    </div>""", unsafe_allow_html=True)


def render_nav_buttons():
    current = st.session_state.ibvap_page
    cols = st.columns(len(PAGES))
    page_icons = {
        "command-center": ":material/dashboard: Command Center",
        "surveillance": ":material/videocam: Surveillance",
        "security-events": ":material/warning: Security Events",
        "digital-evidence": ":material/photo_camera: Digital Evidence",
        "audit-log": ":material/verified_user: Audit Log",
        "system": ":material/settings: System",
    }
    for i, (pid, label) in enumerate(PAGES):
        with cols[i]:
            display_label = page_icons.get(pid, label)
            st.button(
                display_label, key=f"navbtn-{pid}", use_container_width=True,
                type="primary" if current == pid else "secondary",
                on_click=set_page, args=(pid,)
            )


def main():
    if "ibvap_events" not in st.session_state or not st.session_state.ibvap_events:
        st.session_state.ibvap_events = fetch_events()
    events = st.session_state.ibvap_events

    inject_custom_css()
    render_sidebar()
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


if __name__ == "__main__":
    main()