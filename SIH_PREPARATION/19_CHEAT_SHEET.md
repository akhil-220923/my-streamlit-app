# IBVAP — Single-Page Technical Cheat Sheet
## 19. Quick Reference Technical Fact Sheet

---

### Core Project Information
- **Project Name:** IBVAP (Intelligent Border Video Analytics Platform)
- **Domain:** AI Border Surveillance, Intrusion Detection & Cryptographic Cybersecurity
- **Hackathon:** Smart India Hackathon (SIH 2026) — Blockchain & Cybersecurity

---

### Key Technical Parameters

| Component | Technical Detail | Primary Source File |
| :--- | :--- | :--- |
| **Object Detection Model** | Ultralytics YOLO11 (`yolo11s.pt` / `yolo11n.pt`) | `src/main.py` |
| **Detection Class** | Class `0` (`person` class only) | `src/main.py` (`classes=[0]`) |
| **Tracker Algorithm** | ByteTrack (High/Low Conf Score Fusion) | `bytetrack_day3.yaml` |
| **High Track Threshold** | `0.25` (`track_high_thresh`) | `bytetrack_day3.yaml` |
| **Low Track Threshold** | `0.10` (`track_low_thresh`) | `bytetrack_day3.yaml` |
| **New Track Threshold** | `0.30` (`new_track_thresh`) | `bytetrack_day3.yaml` |
| **Track Buffer Memory** | `60 Frames` (approx. 2s memory) | `bytetrack_day3.yaml` |
| **Matching Threshold** | `0.80` (`match_thresh`) | `bytetrack_day3.yaml` |
| **Database Tier 1** | MongoDB Atlas (`IBVAP.intrusion_events`) | `src/app.py` |
| **Database Tier 2 (Fallback)**| Local CSV (`output/intrusion_log.csv`) | `src/app.py` |
| **Database Tier 3 (Fallback)**| Hardcoded Prototype Seed Data | `src/app.py` |
| **Cryptographic Hash Algorithm**| SHA-256 (`hashlib.sha256`) | `src/app.py` |
| **Audit Root Hash File** | `output/audit_root_hash.txt` | `src/app.py` |
| **Blockchain Ledger File** | `output/blockchain_ledger.json` | `src/app.py` |
| **Ledger Architecture** | Single-Node Local Hash-Linked Ledger (4 Blocks) | `output/blockchain_ledger.json` |
| **Frontend Framework** | Streamlit 1.38+ with Plotly & Custom CSS | `src/app.py` / `streamlit_app/` |
| **Deployment Platform** | Streamlit Community Cloud + GitHub | `streamlit_app/requirements.txt` |

---

### 3 Key Metrics / Facts to Memorize

1. **Root Hash:** `441e0fcff3badcfe7705ce8004b5f0189642d3033ccc370ded52b8e0cb9dcb05`
2. **Verified Prototype Events:** 3 Events (`EVT-001` at frame 30, `EVT-002` at frame 108, `EVT-003` at frame 177).
3. **Data Fallback Resilience:** MongoDB Atlas Cloud $\rightarrow$ Local CSV $\rightarrow$ Hardcoded Seed Data.

---

### 3 Key Phrases to Say to Judges

1. *"IBVAP fuses real-time AI vision with cryptographic security auditability."*
2. *"Our ByteTrack score fusion minimizes false alarms by keeping track IDs active across heavy occlusions."*
3. *"We provide zero-downtime multi-tier fallback and cryptographic tamper evidence for border defense."*
